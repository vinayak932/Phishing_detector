from urllib.parse import urlparse
import ipaddress


def finding_ip_address(parsed):
    if parsed.hostname is None:
        return 0

    try:
        ipaddress.ip_address(parsed.hostname)
        return 1
    except ValueError:
        return 0


def feature(url):
    parsed = urlparse(url)

    # Handle URLs without a scheme
    if parsed.hostname is None:
        parsed = urlparse("http://" + url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    features = {
        "URL_length": len(url),
        "hyphen_count": url.count("-"),
        "digit_count": sum(char.isdigit() for char in url),
        "digit_ratio": sum(char.isdigit() for char in url) / len(url) if len(url) > 0 else 0,
        "dot_count": url.count("."),
        "slash_count": url.count("/"),
        "equals_sign_count": url.count("="),
        "question_sign_count": url.count("?"),
        "has_https": 1 if parsed.scheme == "https" else 0,
        "subdomain_count": (
            max(0, len(hostname.split(".")) - 2)
            if finding_ip_address(parsed) == 0
            else 0
        ),
        "has_ip": finding_ip_address(parsed),
        "query_length": len(query),
        "path_length": len(path),
        "at_count": url.count("@"),
        "hostname_digit_count": sum(char.isdigit() for char in hostname),
        "path_digit_count": sum(char.isdigit() for char in path)
    }

    return features