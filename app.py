from flask import Flask, jsonify, render_template, request

import model
from ip_tools import is_valid_ip, lookup_location

app = Flask(__name__)
app.teardown_appcontext(model.close_db)

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/robots")
def robots():
    return jsonify(model.list_robots())


def parse_ping(data):
    """Return (name, private_ip, public_ip), or raise ValueError with a client-facing message."""
    fields = [data.get(key) for key in ("name", "privateIP", "publicIP")]
    if not all(isinstance(v, str) and v.strip() for v in fields):
        raise ValueError("name, privateIP and publicIP are required strings")
    name, private_ip, public_ip = fields
    if not (is_valid_ip(private_ip) and is_valid_ip(public_ip)):
        raise ValueError("invalid IP address")
    return name, private_ip, public_ip


def resolve_location(name, public_ip):
    """Reuse the stored location unless the public IP changed or was never resolved."""
    existing = model.get_robot(name)
    if existing and existing["public_ip"] == public_ip and existing["location"]:
        return existing["location"]
    return lookup_location(public_ip)


@app.post("/api/ping")
def ping():
    try:
        name, private_ip, public_ip = parse_ping(request.get_json(silent=True) or {})
    except ValueError as e:
        return jsonify(error=str(e)), 400

    location = resolve_location(name, public_ip)
    model.upsert_robot(name, private_ip, public_ip, location)
    return jsonify(status="ok")


model.init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3464, debug=True)
