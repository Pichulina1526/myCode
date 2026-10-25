
amicable = [None] * 10001 

def dn (x):
    if x < 2: return 0 
    factors = []
    for i in range(2, (x // 2) + 1):
        if x % i == 0:
            factors.append(i)
            factors.append(x // i)
            
    final = set(factors)
    return sum(final) + 1

for n in range(1, 10001):
    temp = dn(n)
    amicable[n] = [n, temp]
    
total = []
for i in range(2, 10000):
    partner = amicable[i][1]
    
    if 0 < partner <= 10000:
        if partner != i and amicable[partner][1] == i:
            total.append(i)
            total.append(partner)
        
finalset = set(total)
answer = sum(finalset)

print(f"Amicable numbers: {sorted(list(finalset))}")
print(f"Final Answer: {answer}")