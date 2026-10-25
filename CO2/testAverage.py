tests = [[None]*3 for i in range (30)]

for i in range (1,31):
    for u in range(1,4):
        valid = False
        while valid == False:
            test = input(f"enter pupil:{i} test{u} score: ")
            valid1 = False
            while valid1 == False:
                if test != "":
                    valid1 = True
                else:
                    print("you must enter a score")
                    test = input(f"enter pupil:{i} test{u} score: ")
                
                
                
            if int(test) > 0 and int(test) < 100:
                valid = True
                testScore = int(test)
            else:
                print("invalid try again")
                test = input(f"enter pupil:{i} test{u} score: ")
                
        tests[i-1][u-1] = f"pupil:{i} test{u} score = {testScore}"

        
print(tests)