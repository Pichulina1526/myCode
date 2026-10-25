from math import isqrt 

factors = 0
found = False
sequence = 1
numbers = []
for i in range(1000000):
    numbers.append(i)

counter = 2
while found == False:
    term = sequence + numbers[counter]
    sequence = term
    factors = 0
    for i in range(1, (isqrt(term) + 1)):
        if term % i == 0:
            factors += 2

    if factors >= 501:
        print(term)
        found = True
    else:
        counter += 1