counter = 0
num = 0
old = 0
while num != 9999:
    valid = False
    while valid == False:
        num = int(input("enter model number: "))
        length = len(str(num))
        if length == 4:
            valid = True
        else:
            print("invalid try again")
            
            
    if num != 9999:
        counter += 1
        
    if int(str(num)[3]) > 5 and int(str(num)[3]) < 9:
        old += 1
        
print(f"you entered {counter} parts and {old} were old parts")
        
    

        