def http_parse_request(version):
    close_connection = True
    if not version.startswith('HTTP/'):
        return False
    base_version_number = version.split('/', 1)[1]
    version_number = base_version_number.split(".")
        # RFC 2145 section 3.1 says there can be only one "." and
        #   - major and minor numbers MUST be treated as
        #      separate integers;
        #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
        #      turn is lower than HTTP/12.3;
        #   - Leading zeros MUST be ignored by recipients.
    if len(version_number) != 2:
        return False
    version_number_1 = version_number[0]
    version_number_2 = version_number[1]
    if not (version_number_1.isdigit() and version_number_2.isdigit()):
        return False
    version_number_1 = int(version_number[0])
    version_number_2 = int(version_number[1])


    if version_number_1 >= 1 and version_number_2 >= 1:
        return True
    if version_number_1 >= 2 and version_number_2 >= 0:
        return False
    return True

print(http_parse_request("HTTP/1.2"))   # pragma: no cover
