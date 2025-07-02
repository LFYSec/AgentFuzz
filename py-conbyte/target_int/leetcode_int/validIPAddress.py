
# https://leetcode.com/problems/validate-ip-address/discuss/298894/Python3%3A-Simple-code-or-more-than-99-beats

# Write a function to check whether an input string is a valid 
# IPv4 address or IPv6 address or neither.

# IPv4 addresses are canonically represented in dot-decimal notation, 
# which consists of four decimal numbers, each ranging from 0 to 255, 
# separated by dots ("."), e.g.,172.16.254.1; 


# IPv6 addresses are represented as eight groups of four hexadecimal 
# digits, each group representing 16 bits. The groups are separated 
# by colons (":"). For example, the address 
# 2001:0db8:85a3:0000:0000:8a2e:0370:7334 is a valid one.


def validIPAddress(IP: str) -> str:
    if '.' in IP:
        octa = IP.split('.')
        if len(octa) != 4:
            return "Neither"
        for i in octa:
            if not i.isdigit() or int(i) > 255 or( i[0] == '0' and len(i) > 1):
                return "Neither"
        return "IPv4"
    octa = IP.split(":")
    if len(octa) != 8:
        return "Neither"
    for i in octa:
        if len(i) > 4 or len(i) < 1:
            return "Neither"
        for val in i:
            if (val >= 'a' and val <= 'f') or (val >= 'A' and val <= 'F') or (val >= '0' and val <= '9'):
                continue
            else:
                return "Neither"
    return "IPv6"
