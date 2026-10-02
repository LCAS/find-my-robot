#!/usr/bin/env bash
# Installs a systemd timer on this robot that reports its hostname and IPs to Find my Robot.
# Usage: sudo ./install-robot-service.sh [server-url] [interval-minutes]
set -euo pipefail

SERVER_URL="${1:-https://findmyrobot.services.lcas.group}"
INTERVAL_MIN="${2:-5}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }

cat > /usr/local/bin/find-my-robot-ping <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SERVER_URL="$1"

name="$(hostname -s)"
# Source address of the default route, i.e. the IP other machines on the LAN reach us on
private_ip="$(ip -4 route get 1.1.1.1 | sed -n 's/.* src \([0-9.]*\).*/\1/p' | head -n1)"
public_ip="$(curl -fsS --max-time 10 https://api.ipify.org)"

curl -fsS --max-time 10 -X POST "${SERVER_URL%/}/api/ping" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"${name}\",\"privateIP\":\"${private_ip}\",\"publicIP\":\"${public_ip}\"}"
EOF
chmod 755 /usr/local/bin/find-my-robot-ping

cat > /etc/systemd/system/find-my-robot.service <<EOF
[Unit]
Description=Report this robot to Find my Robot
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/find-my-robot-ping ${SERVER_URL}
EOF

cat > /etc/systemd/system/find-my-robot.timer <<EOF
[Unit]
Description=Periodically report this robot to Find my Robot

[Timer]
OnBootSec=30s
OnUnitActiveSec=${INTERVAL_MIN}min
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now find-my-robot.timer
systemctl start find-my-robot.service || echo "Initial ping failed; see: journalctl -u find-my-robot.service" >&2

echo "Installed. Pinging ${SERVER_URL} every ${INTERVAL_MIN} min as '$(hostname -s)'."
