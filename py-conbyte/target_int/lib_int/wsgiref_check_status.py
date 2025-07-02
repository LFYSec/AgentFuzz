

def wsgiref_check_status(status):
    # Implicitly check that we can turn it into an integer:
    status_code = status.split(" ", 1)[0]
    if len(status_code) != 3:
        return 0
    status_int = int(status_code)
    if status_int < 100:
        return 0
    if len(status) < 4 or status[3] != ' ':
        return 0
    
    return 1

print(wsgiref_check_status("200 ok"))   # pragma: no cover
