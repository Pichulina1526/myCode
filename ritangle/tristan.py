import math
'''
results = []

for a in range(100, 1000):
    for b in range(100, 1000):
        for c in range(100, 1000):

            if a + b <= c or a + c <= b or b + c <= a:
                continue

            cosC = (a*a + b*b - c*c) / (2*a*b)
            
            if -1 <= cosC <= 1:

                angleC = math.degrees(math.acos(cosC))

                if abs(angleC - 60) < 1e-9:
                    results.append((f"{a} {b} {c}"))

print(results)
print("Found:", len(results))



import math

results = []

for a in range(100, 1000):
    for b in range(1000):
        for c in range(1000):
            if b < 100:
                b = int(f"{b:03d}")
                
            
            if c < 100:
                c = int(f"{c:03d}")
                
            
            if a + b <= c or a + c <= b or b + c <= a:
                continue

            cosC = (a*a + b*b - c*c) / (2*a*b)
            
            if -1 <= cosC <= 1:

                angleC = math.degrees(math.acos(cosC))

                if abs(angleC - 60) < 1e-9:
                    if b < 100:
                        b = int(f"{b:03d}")
                    if c < 100:
                        c = int(f"{c:03d}")
                    results.append((f"{a} {b} {c}"))

    print(a)


f = open("finalx.txt","w")


for b in results:
    f.write(b)
    f.write("\n")
f.close()

print("DONE")

'''
import math

results = []

for a in range(100, 1000):
    for b in range(1000):
        for c in range(1000):
            # Use original numeric values for calculations
            b_num = b
            c_num = c
            
            if a + b_num <= c_num or a + c_num <= b_num or b_num + c_num <= a:
                continue

            cosC = (a*a + b_num*b_num - c_num*c_num) / (2*a*b_num)
            
            if -1 <= cosC <= 1:
                angleC = math.degrees(math.acos(cosC))

                if abs(angleC - 60) < 1e-9:
                    # Format with padding only when creating output string
                    b_str = f"{b:03d}"
                    c_str = f"{c:03d}"
                    results.append(f"{a} {b_str} {c_str}")
    print(a)                
                    


f = open("finalx.txt","w")


for b in results:
    f.write(b)
    f.write("\n")
f.close()

print("DONE")
