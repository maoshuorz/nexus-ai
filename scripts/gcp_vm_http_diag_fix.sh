#!/usr/bin/env bash
set -euo pipefail

APPLY_FIX=0
CHECK_SSH=0
SERVICE_NAME=""
EXTERNAL_IP=""

usage() {
  cat <<'EOF'
Usage:
  gcp_vm_http_diag_fix.sh [--service <name>] [--external-ip <ip>] [--check-ssh] [--apply]

Description:
  Diagnose and optionally fix common causes of "connection refused" on 80/443 from outside.
  Run this on the VM (serial console or SSH). Default is read-only.

Options:
  --service <name>    Systemd service name to inspect.
  --external-ip <ip>  VM external IP for loopback test to public interface.
  --check-ssh         Also inspect sshd status and port 22 listen.
  --apply             Apply safe firewall fixes (ufw allow + iptables accept rules).
  -h, --help          Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --service)
      SERVICE_NAME="${2:-}"
      shift 2
      ;;
    --external-ip)
      EXTERNAL_IP="${2:-}"
      shift 2
      ;;
    --check-ssh)
      CHECK_SSH=1
      shift
      ;;
    --apply)
      APPLY_FIX=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  SUDO="sudo"
else
  SUDO=""
fi

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

header() {
  echo
  echo "==== $1 ===="
}

run() {
  echo "+ $*"
  "$@"
}

safe_run() {
  "$@" || true
}

check_listeners() {
  header "Listen sockets on 80/443"
  if have_cmd ss; then
    safe_run $SUDO ss -lntp | grep -E '(:80|:443)\b' || echo "No listener found on :80/:443"
  else
    echo "ss not available"
  fi

  if have_cmd lsof; then
    safe_run $SUDO lsof -iTCP -sTCP:LISTEN -n -P | grep -E '(:80|:443)\b' || echo "No lsof listener found on :80/:443"
  else
    echo "lsof not available"
  fi

  local only_loopback=0
  if have_cmd ss; then
    if $SUDO ss -lnt | grep -E '127\.0\.0\.1:80|127\.0\.0\.1:443' >/dev/null 2>&1; then
      if ! $SUDO ss -lnt | grep -E '0\.0\.0\.0:80|0\.0\.0\.0:443|\[::\]:80|\[::\]:443' >/dev/null 2>&1; then
        only_loopback=1
      fi
    fi
  fi

  if [[ $only_loopback -eq 1 ]]; then
    echo "WARN: Service appears to listen only on loopback (127.0.0.1)."
    echo "      Change bind/listen host to 0.0.0.0 (or [::]) and restart the service."
  fi
}

check_service() {
  if [[ -z "$SERVICE_NAME" ]]; then
    return
  fi

  header "Systemd service: ${SERVICE_NAME}"
  safe_run $SUDO systemctl status "$SERVICE_NAME" --no-pager

  header "Recent logs: ${SERVICE_NAME}"
  safe_run $SUDO journalctl -u "$SERVICE_NAME" -n 200 --no-pager
}

check_local_http() {
  header "Local curl checks"
  if have_cmd curl; then
    safe_run curl -I --max-time 5 http://127.0.0.1:80
    safe_run curl -kI --max-time 5 https://127.0.0.1:443
    if [[ -n "$EXTERNAL_IP" ]]; then
      safe_run curl -I --max-time 5 "http://${EXTERNAL_IP}"
      safe_run curl -kI --max-time 5 "https://${EXTERNAL_IP}"
    fi
  else
    echo "curl not available"
  fi
}

check_ufw() {
  if ! have_cmd ufw; then
    return
  fi

  header "UFW status"
  safe_run $SUDO ufw status verbose

  if [[ $APPLY_FIX -eq 1 ]]; then
    echo "Applying UFW allow for 80/tcp and 443/tcp"
    run $SUDO ufw allow 80/tcp
    run $SUDO ufw allow 443/tcp
    safe_run $SUDO ufw status numbered
  fi
}

check_iptables() {
  if ! have_cmd iptables; then
    return
  fi

  header "iptables rules (summary)"
  safe_run $SUDO iptables -S
  safe_run $SUDO iptables -L INPUT -n -v

  header "iptables INPUT rules touching 80/443"
  safe_run $SUDO iptables -S INPUT | grep -E -- '--dport (80|443)\b'

  if [[ $APPLY_FIX -eq 1 ]]; then
    echo "Applying iptables ACCEPT for tcp/80 and tcp/443 at top of INPUT chain"
    if ! $SUDO iptables -C INPUT -p tcp --dport 80 -j ACCEPT >/dev/null 2>&1; then
      run $SUDO iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
    fi
    if ! $SUDO iptables -C INPUT -p tcp --dport 443 -j ACCEPT >/dev/null 2>&1; then
      run $SUDO iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
    fi
    safe_run $SUDO iptables -L INPUT -n -v
    echo "NOTE: Persist iptables changes with your distro method (netfilter-persistent/firewalld)."
  fi
}

check_ssh() {
  if [[ $CHECK_SSH -ne 1 ]]; then
    return
  fi

  header "SSH checks"
  safe_run $SUDO systemctl status ssh --no-pager
  safe_run $SUDO systemctl status sshd --no-pager
  if have_cmd ss; then
    safe_run $SUDO ss -lntp | grep -E '(:22)\b' || echo "No ssh listener found on :22"
  fi
  if [[ -f /etc/ssh/sshd_config ]]; then
    echo "--- /etc/ssh/sshd_config key lines ---"
    safe_run $SUDO grep -E '^(PubkeyAuthentication|PasswordAuthentication|PermitRootLogin|Port|ListenAddress)\b' /etc/ssh/sshd_config
  fi
}

main() {
  header "System info"
  run uname -a
  safe_run $SUDO hostnamectl

  check_listeners
  check_service
  check_local_http
  check_ufw
  check_iptables
  check_ssh

  header "Result guidance"
  echo "1) If no process listens on 0.0.0.0:80/443, fix app bind address and restart app."
  echo "2) If local curl works but external still refused, inspect host firewall rules and GCP firewall/tag mapping."
  echo "3) Re-run this script with --apply to apply safe firewall opens."
}

main
