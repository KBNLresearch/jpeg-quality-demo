myList = [0.2, 0.1, 0.8, 0.3, 0.1, 0.7]

minVal = min(myList)
indices = ['crap' for i, x in enumerate(myList) if x == minVal]

print(indices)