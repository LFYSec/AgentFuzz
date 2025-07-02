
def map2dec(char):
    if char == "a" or char == "A":
        return 10
    elif char == "b" or char == "B":
        return 11
    elif char == "c" or char == "C":
        return 12
    elif char == "d" or char == "D":
        return 13
    elif char == "e" or char == "E":
        return 14
    elif char == "f" or char == "F":
        return 15
    else:
        return int(char)

def hex2int(orig):
    num = 0
    for char in orig:
        n = map2dec(char)
        num = num * 16 + n

    return num

def _parse_hextet(hextet_str):
    _HEX_DIGITS = "0123456789ABCDEFabcdef"
    for char in hextet_str:
        if char not in _HEX_DIGITS:
            return -1
    if len(hextet_str) > 4:
        return -1
    return hex2int(hextet_str)

def ipaddress__ip_int_from_string(ip_str):
    """Turn an IPv6 ip_str into an integer.

    Args:
        ip_str: A string, the IPv6 ip_str.

    Returns:
        An int, the IPv6 address

    Raises:
        AddressValueError: if ip_str isn't a valid IPv6 Address.

    """
    if len(ip_str) == 0:
        return "Empty"

    _HEXTET_COUNT = 8
    parts = ip_str.split(':')

    # An IPv6 address needs at least 2 colons (3 parts).
    _min_parts = 3
    if len(parts) < _min_parts:
        msg = "At least 3 parts expected in ip_addr"
        return msg

    # If the address has an IPv4-style suffix, convert it to hexadecimal.
    # TODO
    if '.' in parts[-1]:
        return "It's IPv4"

    # An IPv6 address can't have more than 8 colons (9 parts).
    # The extra colon comes from using the "::" notation for a single
    # leading or trailing zero part.
    _max_parts = _HEXTET_COUNT + 1
    if len(parts) > _max_parts:
        msg = "At most 7 colons permitted in ip"
        return msg

    # Disregarding the endpoints, find '::' with nothing in between.
    # This indicates that a run of zeroes has been skipped.
    skip_index = 0
    for i in range(1, len(parts) - 1):
        if len(parts[i]) == 0:
            if skip_index != 0: 
                # Can't have more than one '::'
                msg = "At most one '::' permitted in ip"
                return msg
            skip_index = i

    # parts_hi is the number of parts to copy from above/before the '::'
    # parts_lo is the number of parts to copy from below/after the '::'
    if skip_index != 0:
        # If we found a '::', then check if it also covers the endpoints.
        parts_hi = skip_index
        parts_lo = len(parts) - skip_index - 1
        if len(parts[0]) == 0:
            parts_hi -= 1
            if parts_hi:
                msg = "Leading ':' only permitted as part of '::' in ip"
                return msg
        if len(parts[-1]) == 0:
            parts_lo -= 1
            if parts_lo:
                msg = "Trailing ':' only permitted as part of '::' in ip"
                return msg
        parts_skipped = _HEXTET_COUNT - (parts_hi + parts_lo)
        if parts_skipped < 1:
            msg = "Expected at most 7 other parts with '::' in ip"
            return msg
    else:
        # Otherwise, allocate the entire address to parts_hi.  The
        # endpoints could still be empty, but _parse_hextet() will check
        # for that.
        if len(parts) != _HEXTET_COUNT:
            msg = "Exactly 8 parts expected without '::' in ip"
            return msg
        if len(parts[0]) == 0:
            msg = "Leading ':' only permitted as part of '::' in ip"
            return msg
        if len(parts[-1]) == 0:
            msg = "Trailing ':' only permitted as part of '::' in ip"
            return msg
        parts_hi = len(parts)
        parts_lo = 0
        parts_skipped = 0

    # Now, parse the hextets into a 128-bit integer.
    ip_int = 0
    for i in range(parts_hi):
        ip_int *= 65536 
        num = _parse_hextet(parts[i])
        if num < 0:
            return "Error at end"
        ip_int += num
    ip_int <<= 16 * parts_skipped
    for i in range(-parts_lo, 0):
        ip_int *= 65536 
        num = _parse_hextet(parts[i])
        if num < 0:
            return "Error at end"
        ip_int += num
    return ip_int


print(ipaddress__ip_int_from_string("2001:0db8:85a3:0:0:8A2E:0370:7334"))   # pragma: no cover
