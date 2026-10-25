from math import isqrt
from time import perf_counter

N = int(input(""))

a = perf_counter()

sieve = [True] * N
sieve[0] = False
sieve[1] = False

limit = int(isqrt(N)) + 1

for i in range(2, limit):
    if sieve[i]:
        start = i * i
        for multiple in range(start, N , i):
            sieve[multiple] = False

g = perf_counter()

primes =[i for i,prime in enumerate(sieve) if prime]
primes_sum = sum(primes)

total_time = g - a
rate_of_primes = len(primes) / total_time

print(f"∑primes <= {N} = {primes_sum}")
print(f"total time taken = {total_time} seconds")
print(f"rate of primes generated = {rate_of_primes} per second")