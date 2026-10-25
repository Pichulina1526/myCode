
from itertools import permutations



def is_touching(a,b):
    touching = False
    if a == 0:
        if b in [4,3,5,1,2]:
            touching = True
    elif a == 1:
        if b in [0,2,8,7,5]:
            touching = True
    elif a == 2:
        if b in [0,1,8,11,3]:
            touching = True
    elif a == 3:
        if b in [4,10,0,2,11]:
            touching = True
    elif a == 4:
        if b in [0,10,3,5,6]:
            touching = True
    elif a == 5:
        if b in [4,7,6,0,1]:
            touching = True
    elif a == 6:
        if b in [9,7,5,4,10]:
            touching = True
    elif a == 7:
        if b in [5,6,9,8,1]:
            touching = True
    elif a == 8:
        if b in [1,9,11,2,7]:  
            touching = True
    elif a == 9:
        if b in [8,6,10,11,7]:  
            touching = True
    elif a == 10:
        if b in [11,9,6,4,3]:
            touching = True
    elif a == 11:
        if b in [8,2,3,9,10]:
            touching = True
    
    return touching


def D_check(check):
    check1 = list(check)
    Dposition1 = check1.index("D")
    check1[Dposition1] = "z"
    Dposition2 = check1.index("D")
    check1[Dposition2] = "z"
    Dposition3 = check1.index("D")

    touchingD = False
    if is_touching(Dposition1,Dposition2) == True:
        touchingD = True
    elif is_touching(Dposition1,Dposition3) == True:
        touchingD = True
    elif is_touching(Dposition2,Dposition1) == True:
        touchingD = True
    elif is_touching(Dposition2,Dposition3) == True:
        touchingD = True
    elif is_touching(Dposition3,Dposition1) == True:
        touchingD = True
    elif is_touching(Dposition3,Dposition2) == True:
        touchingD = True
        
    if touchingD == True:
        return False
    else:
        return True
    
    
    

def O_check(check):
    check1 = list(check)
    Oposition1 = check1.index("O")
    check1[Oposition1] = "z"
    Oposition2 = check1.index("O")
    
    touchingO = False
    if is_touching(Oposition1,Oposition2) == True:
        touchingO = True
    elif is_touching(Oposition2,Oposition1) == True:
        touchingO = True
    
    return touchingO



    
def valid(string):
    if O_check(string) == True and D_check(string) == True:
        return True
    else:
        return False
    


## main program

counter = 0
total = 0

for perm in permutations("DODECAHEDRON"):
    perm_string = "".join(perm)
    
    if valid(perm_string):
        counter += 1
    
    total += 1
    
    if total % 10000000 == 0:
        print(f"Checked {total:,} permutations and found {counter:,} valid ones so far")




# Calcs
probability = counter / total

print(f"\nTotal: {total:,}")
print(f"Valid : {counter:,}")
print(f"Probability: {probability}")


#Total: 479,001,600
#Valid : 18,144,000
#Probability: 0.03787878787878788