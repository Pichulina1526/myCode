# 1-9
oneToNine = 36

# 10-19
tenToNineteen = 70

# twenty to ninety
tens = 46

twentyToNinetyNine = (10 * tens) + (8 * oneToNine)

sumOneNinetyNine = oneToNine + tenToNineteen + twentyToNinetyNine


# hundred appears 900 times
hundredSum = 900 * 7

# "and" used 891 times
andSum = 891 * 3

# base hundreds ("one" to "nine")
sumBaseHundred = 100 * oneToNine

# 1-99 repeats 9 times in the hundreds
sumHundredNineNinetyNine = (
    hundredSum
    + andSum
    + sumBaseHundred
    + (9 * sumOneNinetyNine)
)

# add 1-99 and "one thousand"
total = sumHundredNineNinetyNine + sumOneNinetyNine + 11

print(total)
