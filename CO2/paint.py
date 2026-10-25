'''Write an algorithm that will calculate the amount of paint required to paint a room. 
The user will enter the dimensions of the room,
the total dimensions of the unpaintable areas (such as windows,
doors or brickwork) and the number of coats of paint required. 
Assume that 1 litre of paint covers 11 sq m.
'''


def paintArea(number):
    sum = 0
    for i in range(1,number+1):
        height = int(input(f"height of wall {i}(in metres): "))
        width = int(input(f"width of wall{i}(in metres): "))
        area = height * width
        sum += area
        
    return sum

def notPaintArea(number):
    sum = 0
    for i in range(1,number):
        height = int(input(f"height of unpaintable area {i}(in metres): "))
        width = int(input(f"width of unpaintable are {i}(in metres): "))
        area = height * width
        sum += area
    
    return sum

wallsN = int(input("how many walls in your room: "))
unPaintN = int(input("how many sections of the room are you not going to paint: "))
coats = int(input("how many coats will you do: "))

result1 = paintArea(wallsN)
result2 = notPaintArea(unPaintN)

totalArea = result1 + result2

metresRequired = totalArea * coats
litresRequired = metresRequired / 11

print(f"you need {litresRequired} litres of paint!")


