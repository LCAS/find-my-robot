# 🤖 Find my Robot

IP Tracker is Back... This is a tool to find robots local IP address's.

The live version of this is available at [FindMyRobot.services.lcas.group](https://findmyrobot.services.lcas.group)

Robots report their hostname and IPv4 addresses to a small Flask app, which shows them in a filterable table with a geo-located public IP and a colour-coded last-ping time.

## Routes

| Route | Description |
|---|---|
| `GET /` | Web page: filterable table (25 rows per page), sorted by last ping, then name, then private IP. Supports light and dark mode. |
| `GET /api/robots` | JSON list of robots. |
| `POST /api/ping` | Robots update their record. Body: `{"name": "Bob", "privateIP": "10.0.0.0", "publicIP": "5.5.5.5"}` |

Last ping colour: green within 10 minutes, orange within 30, red within 60, grey after that.

Location is looked up from the public IP using [ip-api.com](https://ip-api.com) (free tier, HTTP only, rate limited) and cached until the robot's public IP changes.

## Project layout

- `app.py` - Flask routes
- `model.py` - SQLite database access
- `ip_tools.py` - IP validation and location lookup
- `templates/`, `static/` - HTML, CSS (`style.css`) and JS (`app.js`)
- `scripts/install-robot-service.sh` - robot-side installer

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```
uv run app.py
```

Then open http://localhost:3464. Data is stored in `robots.db` (override with `DB_PATH`).

Robots not seen for 14 days are deleted automatically (override with `RETENTION_DAYS`).

## Container

```
docker build -t find-my-robot .
docker run -p 3464:3464 -v robots:/data find-my-robot
```

The image is Alpine based, runs gunicorn as a non-root user and stores its database in `/data`. A GitHub workflow publishes it to `ghcr.io/lcas/find-my-robot`.

## Robot setup

On each robot, run as root:

```
curl -fsSL https://raw.githubusercontent.com/lcas/find-my-robot/main/scripts/install-robot-service.sh | sudo bash
```

Defaults are `https://findmyrobot.services.lcas.group` and 5 minutes, so leave them out for simplicity. The script installs a systemd service and timer (`find-my-robot.service` / `find-my-robot.timer`) that POST to `/api/ping` using:

- name: the robot's short hostname
- privateIP: source address of the default route
- publicIP: from `https://api.ipify.org`

Check status with `systemctl list-timers find-my-robot.timer` and `journalctl -u find-my-robot.service`.
