list = [3, 7, 9, 12, 15,4,10,11,20,25]

want = int(input("pattern"))
shush = False
for i in range(len(list)):
    if list[i] == want:
        print(f"found at index {i}")
        shush = True
        
if shush == False:
    print("cut bro")
