import os
with open("extra.txt", "w") as file:
    # Times tables 1 to 15
    for i in range(1, 16):
        for u in range(1, 16):
            ans = i * u
            file.write(f"'{i} x {u}'\n?\n'{ans}'\n\n\n\n")

    # Square numbers up to 30
    for i in range(1, 31):
        ans = i ** 2
        file.write(f"'{i}^2'\n??\n'{ans}'\n\n\n\n")

    # Cubes up to 10
    for i in range(1, 11):
        ans = i ** 3
        file.write(f"'{i}^3'\n??\n'{ans}'\n\n\n\n")

    # Powers of 2 up to 10
    for i in range(1, 11):
        ans = 2 ** i
        file.write(f"'2^{i}'\n??\n'{ans}'\n\n\n\n")

    # Powers of 3 up to 5
    for i in range(1, 6):
        ans = 3 ** i
        file.write(f"'3^{i}'\n??\n'{ans}'\n\n\n\n")

print("Done! Right-click extra.txt and select 'Reload from Disk'")