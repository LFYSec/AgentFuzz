
def loop(a, b):
    arr = [a, a, b, a, a, a]
    cnt = 0
    for ele in arr:
        if ele > 1:
            break
        cnt += ele
    return cnt

