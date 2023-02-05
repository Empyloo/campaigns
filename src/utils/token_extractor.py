from typing import Optional


def extract_token_from_header(headers) -> Optional[str]:
    authorization_header = headers.get("Authorization")
    if not authorization_header:
        return "Error: No Authorization header found: %s" % headers

    header_parts = authorization_header.split(" ")
    if len(header_parts) != 2 or header_parts[0] != "Bearer":
        return "Error: Invalid Authorization header, more than 2 parts: %s" % headers

    return header_parts[1]
