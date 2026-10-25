

def getPword(attempt):
    if attempt == 1:
        password = input("enter password: ")
        while len(password) < 6 or len(password) > 8:
            password = input("inavlid length(must be between 6 abd 8 characters), enter password: ")
            
    elif attempt == 2:
        password = input("re-enter password: ")
        if len(password) < 6 or len(password) > 8:
            print("password do not match - try again")
            
    return password

match = False
while match == False:            
    if getPword(1) == getPword(2):
        print("passwords match!")
        match = True
    else:
        match = False