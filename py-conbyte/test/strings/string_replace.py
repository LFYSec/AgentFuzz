
# Test replace
def string_replace(a, b):
    c = a.replace("A,", "!", 40)
    d = b.replace(" ", "", 1)
    if 'ABC' in c:
        return 0
    elif " " in d:
        return 1
    else:
        return 2

