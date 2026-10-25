def longest(string1):
    max_count = 0
    count = 0
    for x in string1:
        if x == 'C':
            count += 1
            if count > max_count:
                max_count = count
        else:
            count = 0
    return max_count

result = longest("aaaaCCCCaaaaCCCCCCCCaaC")
print(result)