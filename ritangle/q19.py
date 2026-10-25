primes = [2]
for i in range(3, 99):
    prime = True
    for u in range(2, i):
        if i % u == 0:
            prime = False
    if prime:
        primes.append(i)
        
even = [2]
for i in range(4, 99, 2):  
    even.append(i)
    
total = len(primes) * len(even)  
bone = 0

for P in primes:
    for E in even:
        for n in range(1, 10000): 
            Primrose = P + (n-1) * E   
            Eve = (1000 * E) - (n-1) * P  
            
            if Primrose == Eve:
                bone += 1
                
answer = bone / total
print(answer)