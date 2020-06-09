def octToDecimal(n):
  num = n 
  dec_value = 0
  base = 1

  temp = num; 
  while (temp): 
    last_digit = temp % 10 
    temp = int(temp / 10)
    dec_value += last_digit * base; 

    base = base * 8; 

  return dec_value;

def check(string):
  return all(c in string.hexdigits for c in string)

def octop(num1, num2, op):
  if check(str(num1)) and check(str(num2)):
    num1 = octToDecimal(str(num1))
    num2 = octToDecimal(str(num2))

    if op == '+':
      return oct(num1 + num2)
    elif op == '-':
      return oct(num1 - num2)
    elif op == '*':
      return oct(num1 * num2)
    elif op == '/':
      try:
        return oct(num1 / num2)
      except ZeroDivisionError:
        print('Not Divisible by zero')
    else:
      return "Invalid Octal Number"
