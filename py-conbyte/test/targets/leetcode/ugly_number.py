
# 263_Ugly_Number

def ugly_number(num):
    if num <= 0:
        return False
    divisors = [2, 3, 5]
    for d in divisors:
        while num % d == 0:
            num = int(num / d)
    return num == 1

print(ugly_number(-2147483648)) # pragma: no cover
print(ugly_number(8))           # pragma: no cover
