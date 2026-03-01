#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=""
ZONE=""
INSTANCE=""
RULE_NAME="allow-web-80-443"
TARGET_TAG="web"
SOURCE_RANGE="0.0.0.0/0"
PRIORITY="1000"
APPLY=0

usage() {
  cat <<'EOF'
Usage:
  gcp_firewall_web_fix.sh --project <id> --zone <zone> --instance <name> [options]

Options:
  --project <id>       GCP project id (required)
  --zone <zone>        VM zone (required), e.g. asia-east1-b
  --instance <name>    VM instance name (required)
  --rule-name <name>   Firewall rule name (default: allow-web-80-443)
  --target-tag <tag>   Network tag for VM and firewall target (default: web)
  --source-range <cidr> Source IPv4 CIDR (default: 0.0.0.0/0)
  --priority <num>     Firewall rule priority (default: 1000)
  --apply              Apply changes. Without this flag, script is read-only.
  -h, --help           Show help.

Examples:
  ./gcp_firewall_web_fix.sh --project my-proj --zone asia-east1-b --instance web-1
  ./gcp_firewall_web_fix.sh --project my-proj --zone asia-east1-b --instance web-1 --apply
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT_ID="${2:-}"
      shift 2
      ;;
    --zone)
      ZONE="${2:-}"
      shift 2
      ;;
    --instance)
      INSTANCE="${2:-}"
      shift 2
      ;;
    --rule-name)
      RULE_NAME="${2:-}"
      shift 2
      ;;
    --target-tag)
      TARGET_TAG="${2:-}"
      shift 2
      ;;
    --source-range)
      SOURCE_RANGE="${2:-}"
      shift 2
      ;;
    --priority)
      PRIORITY="${2:-}"
      shift 2
      ;;
    --apply)
      APPLY=1
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

if [[ -z "$PROJECT_ID" || -z "$ZONE" || -z "$INSTANCE" ]]; then
  echo "ERROR: --project, --zone, --instance are required" >&2
  usage
  exit 1
fi

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command not found: $1" >&2
    exit 1
  fi
}

run() {
  echo "+ $*"
  "$@"
}

maybe_run() {
  if [[ $APPLY -eq 1 ]]; then
    run "$@"
  else
    echo "[dry-run] $*"
  fi
}

need_cmd gcloud

echo "Checking active gcloud account..."
ACTIVE_ACCT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' || true)"
if [[ -z "$ACTIVE_ACCT" ]]; then
  echo "ERROR: no active gcloud account. Run: gcloud auth login" >&2
  exit 1
fi
echo "Active account: $ACTIVE_ACCT"

echo
echo "Describing instance ${INSTANCE}..."
NETWORK="$(gcloud compute instances describe "$INSTANCE" \
  --project "$PROJECT_ID" \
  --zone "$ZONE" \
  --format='get(networkInterfaces[0].network)' || true)"
EXTERNAL_IP="$(gcloud compute instances describe "$INSTANCE" \
  --project "$PROJECT_ID" \
  --zone "$ZONE" \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)' || true)"
CURRENT_TAGS="$(gcloud compute instances describe "$INSTANCE" \
  --project "$PROJECT_ID" \
  --zone "$ZONE" \
  --format='get(tags.items)' || true)"

echo "External IP: ${EXTERNAL_IP:-<none>}"
echo "Network URI: ${NETWORK:-<unknown>}"
echo "Current tags: ${CURRENT_TAGS:-<none>}"

if [[ -z "$EXTERNAL_IP" ]]; then
  echo "WARN: instance has no external IP. External direct access will not work."
fi

echo
echo "Checking instance tag '${TARGET_TAG}'..."
if gcloud compute instances describe "$INSTANCE" \
  --project "$PROJECT_ID" \
  --zone "$ZONE" \
  --format='get(tags.items)' | tr ',;' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -Fx "$TARGET_TAG" >/dev/null; then
  echo "Tag '${TARGET_TAG}' already present"
else
  maybe_run gcloud compute instances add-tags "$INSTANCE" \
    --project "$PROJECT_ID" \
    --zone "$ZONE" \
    --tags "$TARGET_TAG"
fi

echo
echo "Checking firewall rule '${RULE_NAME}'..."
if gcloud compute firewall-rules describe "$RULE_NAME" --project "$PROJECT_ID" >/dev/null 2>&1; then
  echo "Rule exists. Ensuring allow tcp:80,tcp:443 and target tag '${TARGET_TAG}'."
  maybe_run gcloud compute firewall-rules update "$RULE_NAME" \
    --project "$PROJECT_ID" \
    --allow tcp:80,tcp:443 \
    --source-ranges "$SOURCE_RANGE" \
    --target-tags "$TARGET_TAG" \
    --priority "$PRIORITY"
else
  maybe_run gcloud compute firewall-rules create "$RULE_NAME" \
    --project "$PROJECT_ID" \
    --direction INGRESS \
    --action ALLOW \
    --rules tcp:80,tcp:443 \
    --source-ranges "$SOURCE_RANGE" \
    --target-tags "$TARGET_TAG" \
    --priority "$PRIORITY"
fi

echo
echo "Final firewall rule view:"
if [[ $APPLY -eq 1 ]]; then
  run gcloud compute firewall-rules describe "$RULE_NAME" --project "$PROJECT_ID"
else
  echo "[dry-run] gcloud compute firewall-rules describe ${RULE_NAME} --project ${PROJECT_ID}"
fi

echo
echo "Validation commands:"
echo "  nc -vz ${EXTERNAL_IP:-<external-ip>} 80"
echo "  nc -vz ${EXTERNAL_IP:-<external-ip>} 443"
echo "  curl -I http://${EXTERNAL_IP:-<external-ip>}"
