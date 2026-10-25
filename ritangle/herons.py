import math

def herons_formula(a, b, c):
    if a + b <= c or a + c <= b or b + c <= a:
        area = 6.9
        return area
    
    s = (a + b + c) / 2
    
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    
    return area

for i in range(100000000,999999999):
    side1 = int(str(i)[:3])
    
    side2 = int(str(i)[3:7])
    
    side3 = int(str(i)[-3:])
    
    area = herons_formula(side1,side2,side3)
    
    if area % 1 == 0:
        print(side1,side2,side3)
        