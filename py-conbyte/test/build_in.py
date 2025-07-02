
def build_in(a, b):
    array = [1, 2, 3, a, b]

    summing = sum(array)
    do_max = max(a, 100)
    do_min = min(b, 0)
    summing += do_min

    if summing > do_max:
        return 0
    else:
        return 1
