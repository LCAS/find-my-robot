import ipaddress

import requests


def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def lookup_location(ip):
    """Query ip-api.com (free, no key) for a human-readable location."""
    try:
        if ipaddress.ip_address(ip).is_private:
            return "Private network"
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,city,regionName,country"},
            timeout=3,
        )
        data = r.json()
        if data.get("status") != "success":
            return None
        return ", ".join(p for p in (data.get("city"), data.get("regionName"), data.get("country")) if p)
    except (requests.RequestException, ValueError):
        return None
