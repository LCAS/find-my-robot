import ipaddress

import requests


def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


UNKNOWN_FLAG = "\U0001F3F4\u200D\u2620\uFE0F"  # pirate flag


def flag_emoji(country_code):
    # Regional indicator symbols: 'A'..'Z' map to U+1F1E6..U+1F1FF
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in country_code.upper())


def lookup_location(ip):
    """Query ip-api.com (free, no key) and return e.g. '🇬🇧 Lincoln, England'."""
    try:
        if ipaddress.ip_address(ip).is_private:
            return f"{UNKNOWN_FLAG} Private network"
        r = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,city,regionName,countryCode"},
            timeout=3,
        )
        data = r.json()
        if data.get("status") != "success":
            return f"{UNKNOWN_FLAG} Unknown"
        place = ", ".join(p for p in (data.get("city"), data.get("regionName")) if p)
        return f"{flag_emoji(data['countryCode'])} {place or 'Unknown'}"
    except (requests.RequestException, ValueError, KeyError):
        return f"{UNKNOWN_FLAG} Unknown"
