winner = ""
P1turn = True
P2turn = False
finished = False
total = 0

def playTurn(playerNumber):
    global total, finished, winner, P1turn, P2turn  # ← add this
    number = 0
    while number < 1 or number > 3:
        number = int(input("enter amount"))
        
    print(f"{playerNumber} turn:")
    for i in range (number):
        total += 1
        print(total)
        if total == 15:
            finished = True
            winner = playerNumber
            break
        
    if P1turn:
        P2turn = True
        P1turn = False
    else:
        P1turn = True
        P2turn = False
        
        
        
while finished != True:
    if P1turn == True:
        playTurn("player1")
    else:
        playTurn("player2")
        
print(f"{winner} wins")
    