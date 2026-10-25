
table = [[""] for _ in range(100)]

def hash_function(word):
    total = 0
    for i, c in enumerate(word):
        total += ord(c) * (31 ** i)

    final = total % len(table)
    return final

def add():
    word = input("enter your word to add: ")
    hash_val = hash_function(word)
    if word in table[hash_val]:
        print(f"this item already exists in position {hash_val}")
    elif table[hash_val][0] == "":
        table[hash_val][0] = word
        print(f"your item has been successfully stored at position {hash_val}")
    else:
        table[hash_val].append(word)
        print(f"your item has been successfully stored at position {hash_val}")



def remove():
    word = input("enter your word to remove: ")
    hash_val = hash_function(word)
    found = False
    for i in range(len(table[hash_val])):
        if table[hash_val][i] == word:
            table[hash_val][i] = ""
            found = True
            break
    if found:
        print(f"your item has been removed from position {hash_val}")
    else:
        print("your item is not in this table")


def find():
    word = input("which word are you looking for: ")
    hash_val = hash_function(word)
    found = False
    for word1 in table[hash_val]:
        if word1 == word:
            print(f"your item has been found in position {hash_val}")
            found = True

    if not found:
        print("your item is not in this table")


# main

finished = False
while not finished:
    good = False
    choice = ""
    while not good:
        choice = input("would you like to add(1) or remove(2) or find(3) or exit(4)? ")
        if not choice.isdigit():
            print("enter valid number" )
        elif int(choice) < 1 or int(choice) > 4:
            print("enter valid number")
        else:
            good = True
            choice = int(choice)

    if choice == 1:
        add()
    elif choice == 2:
        remove()
    elif choice == 3:
        find()
    else:
        finished = True