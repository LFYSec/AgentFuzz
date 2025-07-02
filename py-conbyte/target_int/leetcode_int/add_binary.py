
# 067_Add_Binary

# Given two binary strings, return their sum (also a binary string).
# The input strings are both non-empty and contains only characters 1 or 0.

def div_rem(dividend, divider):
    div_c = 0
    orig = dividend
    while orig >= divider:
        orig -= divider
        div_c += 1
    return div_c, orig



def add_binary(a, b):
    res = ''
    lsa, lsb = len(a), len(b)
    pos, plus, curr = -1, 0, 0
    # plus a[pos], b[pos] and curr % 2
    while (lsa + pos) >= 0 or (lsb + pos) >= 0:
        if (lsa + pos) >= 0:
            curr += int(a[pos])
        if (lsb + pos) >= 0:
            curr += int(b[pos])
        div, rem = div_rem(curr, 2)
        res = str(rem) + res
        curr = div 
        pos -= 1
    if curr == 1:
        res = '1' + res
    return res

print(add_binary("10111", "111"))   # pragma: no cover
