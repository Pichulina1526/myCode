longest = 0
best = 0

for i in range(13, 1_000_000):
    counter = 1
    num = i

    while num != 1:
        if num % 2 == 0:
            num //= 2
        else:
            num = 3 * num + 1
        counter += 1

    if counter > longest:
        longest = counter
        best = i

print(f"Longest chain length: {longest}")
print(f"Starting number: {best}")

## answer = 837799