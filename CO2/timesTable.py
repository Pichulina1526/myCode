name = input("enter name: ")
timesTable = int(input("enter times table: "))
startNumber = int(input("enter start multiplier: "))
endNumber = int(input("enter final multiplier: "))

def multiples(name, timesTable, startNumber, endNumber):
    print(f"Hi {name} ... here are your {timesTable} times tables")
    for i in range (startNumber, endNumber + 1):
        print(f"{timesTable} * {i} = {timesTable * i}")
        
        
multiples(name, timesTable, startNumber, endNumber)