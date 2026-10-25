from functools import lru_cache

@lru_cache(None)
def routes(i, j, n=20):
    if i == n and j == n:
        return 1
    if i > n or j > n:
        return 0
    return routes(i + 1, j, n) + routes(i, j + 1, n)

print(routes(0, 0))

# answer = 137846528820