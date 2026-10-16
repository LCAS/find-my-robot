import json
import yaml

from flask import Flask, Response, jsonify, render_template, request

import model
from ip_tools import is_valid_ip, lookup_ip_info

app = Flask(__name__)
app.teardown_appcontext(model.close_db)

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/robots")
def robots():
    return jsonify(filter_robots(model.list_robots(), request.args.get("filter")))


def filter_robots(robots, query):
    """Case-insensitive substring match on name."""
    query = (query or "").strip().lower()
    if not query:
        return robots
    return [r for r in robots if query in str(r["name"] or "").lower()]

@app.get("/api/inventory")
def inventory():
    robots = filter_robots(model.list_robots(), request.args.get("filter"))
    hosts = {r["name"]: {"ansible_host": r["privateIP"]} for r in robots}
    return Response(
        yaml.safe_dump({"all": {"hosts": hosts, "ansible_user": "admin", "ansible_password": "hunter2"}}, sort_keys=False),
        mimetype="text/yaml",
        headers={"Content-Disposition": 'attachment; filename="inventory.yml"'},
    )
    
def parse_ping(data):
    """Return (name, private_ip, public_ip), or raise ValueError with a client-facing message."""
    fields = [data.get(key) for key in ("name", "privateIP", "publicIP")]
    if not all(isinstance(v, str) and v.strip() for v in fields):
        raise ValueError("name, privateIP and publicIP are required strings")
    name, private_ip, public_ip = fields
    if not (is_valid_ip(private_ip) and is_valid_ip(public_ip)):
        raise ValueError("invalid IP address")
    return name, private_ip, public_ip


def resolve_ip_info(name, public_ip):
    """Reuse stored ipinfo data unless the IP changed or needs migrating."""
    existing = model.get_robot(name)
    if (
        existing
        and existing["public_ip"] == public_ip
        and existing["ipinfo_checked"]
    ):
        return existing["location"], existing["asn"]
    return lookup_ip_info(public_ip)


@app.post("/api/ping")
def ping():
    try:
        name, private_ip, public_ip = parse_ping(request.get_json(silent=True) or {})
    except ValueError as e:
        return jsonify(error=str(e)), 400

    location, asn = resolve_ip_info(name, public_ip)
    model.upsert_robot(name, private_ip, public_ip, location, asn)
    return jsonify(status="ok")


model.init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3464, debug=True)
