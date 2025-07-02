# 415_Add_Strings.py

# Add up the inputs 
# and determine if the sum is longer than both inputs

def addStrings(num1, num2):
    """
    :type num1: str
    :type num2: str
    :rtype: str
    """
    if len(num1) == 0 or int(num1) <= 0:
        num1 = '0'
    if len(num2) == 0 or int(num2) <= 0:
        num2 = '0'
    res = []
    carry = 0
    ls = min(len(num1), len(num2))
    pos = -1
    while pos + ls >= 0:
        curr = int(num1[pos]) + int(num2[pos]) + carry
        if curr >= 10:
            res.insert(0, str(curr - 10))
            carry = 1 
        else:
            res.insert(0, str(curr))
            carry = 0 
        pos -= 1
    while pos + len(num1) >= 0:
        curr = int(num1[pos]) + carry
        if curr >= 10:
            res.insert(0, str(curr - 10))
            carry = 1 
        else:
            res.insert(0, str(curr))
            carry = 0 
        pos -= 1
    while pos + len(num2) >= 0:
        curr = int(num2[pos]) + carry
        if curr >= 10:
            res.insert(0, str(curr - 10))
            carry = 1 
        else:
            res.insert(0, str(curr))
            carry = 0 
        pos -= 1
    if carry != 0:
        res.insert(0, str(carry))

    ret = ""
    for r in res:
        ret += r

    l_len = max(len(num1), len(num2))
    if len(ret) > l_len:
        return True
    else:
        return False

print(addStrings("923", "123"))   # pragma: no cover
