list = ["I", "H", "G", "F", "E", "D", "C", "B", "A", "J"]
orderList = []

for i in range(len(list)):
    newItem = list[i]
    
    if len(orderList) == 0:
        orderList.append(newItem)
    else:
        inserted = False
        for u in range(len(orderList)):
            if ord(newItem) < ord(orderList[u]):
                orderList.insert(u, newItem)
                inserted = True
                break  

        if inserted == False:
            orderList.append(newItem)

for i in range(len(orderList)):
    print(orderList[i])