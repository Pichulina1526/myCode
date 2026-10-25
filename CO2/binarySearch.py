list = [3,4,7,9,10,11,12,15,20,25]

target = int(input(""))

def midPoint(x):
    if len(x) % 2 == 0:
        mp = (len(x) - 1) // 2
        return mp
    else:
        mp = len(x) // 2
        return mp
        
offset = 0
found = False
while found == False:
    if len(list) == 0:
        print("not found")
        break
        
    midPointList = midPoint(list)
    midValue = list[midPointList]
    if midValue == target:
        found = True
        print(f"the target has been found at index {midPointList + offset}")
    elif target < midValue:
        list = list[:midPointList]           
    elif target > midValue:
        offset += midPointList + 1
        list = list[midPointList + 1:]
        
            