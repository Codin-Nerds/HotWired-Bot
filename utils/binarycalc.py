def decimalToBinary(n):
    return bin(n).replace("0b", "")


def binaryToDecimal(n):
    return int(n, 2)


def check(string):
    p = set(string)
    s = {"0", "1"}

    if s == p or p == {"0"} or p == {"1"}:
        return True

    else:
        return False


def binaryop(num1, num2, op):
    if check(str(num1)) and check(str(num2)):
        num1 = binaryToDecimal(str(num1))
        num2 = binaryToDecimal(str(num2))

        if op == "+":
            return decimalToBinary(num1 + num2)
        elif op == "-":
            return decimalToBinary(num1 - num2)
        elif op == "*":
            return decimalToBinary(num1 * num2)
        elif op == "/":
            try:
                return decimalToBinary(num1 / num2)
            except ZeroDivisionError:
                print("Not Divisible by zero")
        else:
            return "Invalid Binary Number"
