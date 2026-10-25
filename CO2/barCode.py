from random import randint as ri

codes = []
for i in range (100):
    codes.append(ri(1,999999))
    
def check_digit_calc(code):
    sum = 0
    for i in range(len(str(code)) - 1):
        sum += int(str(code)[i])
        
    sum = sum * 3
    
    bone = sum % 10
    
    return bone
  
  
counter = 0
    
for i in range (len(codes)):
    barcode = codes[i]
    last_digit = int(str(barcode)[-1])
    check_digit = check_digit_calc(barcode)
    if check_digit == last_digit:
        counter += 1
        
        
print(f"there are {counter} correct barcodes")