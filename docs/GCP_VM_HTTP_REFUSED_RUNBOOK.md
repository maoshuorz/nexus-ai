# GCP VM 80/443 Connection Refused Runbook

This runbook implements the troubleshooting plan with executable scripts.

## Files

- `scripts/gcp_vm_http_diag_fix.sh`: run on the VM (serial console or SSH).
- `scripts/gcp_firewall_web_fix.sh`: run on your local machine with `gcloud`.

## 1) VM-side diagnostics first

Run on the VM:

```bash
chmod +x scripts/gcp_vm_http_diag_fix.sh
sudo scripts/gcp_vm_http_diag_fix.sh --service <your-systemd-service> --external-ip <external-ip> --check-ssh
```

If output shows only `127.0.0.1:80` / `127.0.0.1:443`, update your app bind host to `0.0.0.0` and restart service.

If host firewall blocks 80/443, apply safe opens:

```bash
sudo scripts/gcp_vm_http_diag_fix.sh --service <your-systemd-service> --external-ip <external-ip> --check-ssh --apply
```

## 2) GCP firewall + tag alignment

Run locally (where `gcloud` is authenticated):

```bash
chmod +x scripts/gcp_firewall_web_fix.sh
./scripts/gcp_firewall_web_fix.sh \
  --project <project-id> \
  --zone <zone> \
  --instance <instance-name>
```

The command above is dry-run. To apply:

```bash
./scripts/gcp_firewall_web_fix.sh \
  --project <project-id> \
  --zone <zone> \
  --instance <instance-name> \
  --apply
```

Default behavior:
- Ensures instance has tag `web`.
- Ensures ingress allow rule `allow-web-80-443` for `tcp:80,tcp:443`.
- Source range defaults to `0.0.0.0/0` (tighten later if needed).

## 3) Validation

From your local machine:

```bash
nc -vz <external-ip> 80
nc -vz <external-ip> 443
curl -I http://<external-ip>
```

From the VM:

```bash
sudo ss -lntp | grep -E '(:80|:443)\b'
curl -I http://127.0.0.1:80
curl -kI https://127.0.0.1:443
```

## Notes

- If no external IP exists, direct internet access to the VM will fail by design.
- If VM local curl succeeds but external still fails, re-check GCP firewall target tag mapping.
- If VM uses `firewalld` instead of `ufw/iptables`, add 80/443 there as well.
