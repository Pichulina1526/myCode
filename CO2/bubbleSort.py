list = [ "I", "H", "G", "F", "E", "D", "C", "B", "A", "J"]

loops = 0

sorted = False
while sorted == False:
    sorted = True
    for i in range(len(list) - 1):
        x = i + 1
        temp = ""
        if ord(list[i]) > ord(list[i+1]):
            temp = list[i]
            list.pop(i)
            list.insert(x,temp)
            sorted = False
            loops += 1
            
for i in range(len(list)):
    print(list[i])

print(loops)