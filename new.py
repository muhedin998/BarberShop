import random 
br = 0
while True:
    c = random.randint(1,999999)
    br += 1
    if c == 151765:
        print(f"Number found with {br} tries")
        break
    print(c)