def toBinary(integer):
    if integer == 0:
        return "0"
    if integer == 1:
        return "1"
    
    return f"{toBinary(integer // 2)}{str(integer % 2)}"

num =int(input("enter number to convert"))
print(f"{num} is {toBinary(num)} in binary")