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


def lookup_ip_info(ip):
    """Query ipinfo.io once and return the formatted location and numeric ASN."""
    try:
        if ipaddress.ip_address(ip).is_private:
            return f"{UNKNOWN_FLAG} Private network", None

        response = requests.get(
            f"https://ipinfo.io/{ip}/json",
            timeout=3,
        )
        response.raise_for_status()
        data = response.json()

        country_code = data.get("country")
        if country_code:
            place = ", ".join(
                p for p in (data.get("city"), data.get("region")) if p
            )
            location = f"{flag_emoji(country_code)} {place or 'Unknown'}"
        else:
            location = f"{UNKNOWN_FLAG} Unknown"

        org = data.get("org", "")
        as_number = org.split(maxsplit=1)[0] if org else ""
        asn = as_number[2:] if as_number.startswith("AS") and as_number[2:].isdigit() else None
        return location, asn

    except (requests.RequestException, ValueError, KeyError):
        return f"{UNKNOWN_FLAG} Unknown", None
