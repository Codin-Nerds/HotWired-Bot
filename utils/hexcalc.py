def hexToDecimal(n): 
    return int(n, 16) 

def check(string):
  return all(c in string.hexdigits for c in string)

def hexop(num1, num2, op):
  if check(str(num1)) and check(str(num2)):
    num1 = hexToDecimal(str(num1))
    num2 = hexToDecimal(str(num2))

    if op == '+':
      return hex(num1 + num2)
    elif op == '-':
      return hex(num1 - num2)
    elif op == '*':
      return hex(num1 * num2)
    elif op == '/':
      try:
        return hex(num1 / num2)
      except ZeroDivisionError:
        print('Not Divisible by zero')
    else:
      return "Invalid hexadecimal Number"

