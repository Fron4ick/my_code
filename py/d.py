def delitely(x):
    list_delitely = list()
    for delitel in range(1, x + 1):
        if x % delitel == 0:
            list_delitely.append(delitel)
    return list_delitely


for i in range(1, 100 + 1):
    delitely_i = delitely(i)
    if len(delitely_i) >= 10:
        print(i)

print('Hello, привет!')
