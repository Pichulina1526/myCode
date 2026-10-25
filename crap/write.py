
def competitionWinner():
    number = input("enter phone number")
    if number[0] == "0":
        with open("winner.txt","w") as f:
            f.write(number)

competitionWinner()