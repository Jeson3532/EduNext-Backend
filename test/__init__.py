a = ['a', 'b', 'c']
b = ['a', 'c']
c = [i in a for i in b]
if all(c):
    print(1)