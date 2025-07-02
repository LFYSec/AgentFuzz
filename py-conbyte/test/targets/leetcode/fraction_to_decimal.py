
# 166_Fraction_to_Recurring_Decimal
def fraction_to_decimal(numerator, denominator):
    """
    :type numerator: int
    :type denominator: int
    :rtype: str
    """
    if numerator == 0 or denominator == 0:
        return '0'
    fraction = ''
    if (numerator < 0) ^ (denominator < 0):
        fraction += '-'
    dividend = abs(numerator)
    divisor = abs(denominator)
    fraction += str(int(dividend / divisor))
    remainder = dividend % divisor
    if remainder == 0:
        return fraction
    fraction += '.'
    dic = {}
    while remainder != 0:
        if remainder in dic:
            fraction = fraction[:dic[remainder]] + '(' + fraction[dic[remainder]:] + ')'
            break
        dic[remainder] = len(fraction)
        remainder *= 10
        fraction += str(int(remainder / divisor))
        remainder %= divisor
    return fraction

print(fraction_to_decimal(-50, 8))  # pragma: no cover
