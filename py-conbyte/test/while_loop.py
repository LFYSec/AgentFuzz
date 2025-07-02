
def while_loop(a, b):
    i = 0
    j = 0
    cnt = 0
    while i < 3:
        j = 0
        while j < 3:
            cnt += 1
            j += 1
        i += 1

    return cnt
