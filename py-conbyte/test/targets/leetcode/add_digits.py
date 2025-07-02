
# 258_Add_Digits
def add_digits(num):
    # https://leetcode.com/problems/add-digits/discuss/301549/Python-O(1)-solution-36ms
    if num<9:
        return num
    elif num%9==0:
        return 9
    else:
        return num%9



print(add_digits(38))   # pragma: no cover
