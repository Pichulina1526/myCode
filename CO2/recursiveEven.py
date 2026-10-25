

def even(n):
    if n == 0:
        print("")
    
    if n % 2 == 0 and n != 0:
        print(n)
        even(n-2)
        
    if n % 2 == 1:
        even(n-1)
        
    
num = int(input("enter number"))
even(num)