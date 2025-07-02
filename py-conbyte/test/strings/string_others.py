
# Can't find counterexample of these
def string_others(a, b):
    low = a.lower()
    cnt = b.count(',')
    c = b.strip()
    d = c.split(",")[0]
    if "a" in d:
        return cnt
    else:
        return low.count('a')
