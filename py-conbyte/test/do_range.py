
def do_range(a, b):
    cnt = 0
    for i in range(b, a):
        for j in range(1, 4):
            for k in range(1, 4):
                cnt += 1
    d = cnt
    return d
