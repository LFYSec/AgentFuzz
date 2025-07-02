def multiplication_or_sum(num1, num2):
  product = num1 *num2
  if(product < 1000):
    return product
  else:
    return num1 +num2


print(multiplication_or_sum(10, 20))
