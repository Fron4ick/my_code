k = True
tabt = list()
tabf = list()
st = 0
for r in open(r"C:\Users\f_roz\OneDrive\Documents\my_code\py\tabl\tab1.txt").readlines():
    array = list(map(int, r.split()))
    for i in range(len(array)):
        if array[i] == 1:  # Проверяем значение элемента, а не индекс
            tabt.append(f'{st}X{i}')
        else:
            tabf.append(f'{st}X{i}')
    st += 1

print("True values (1):")
for i in tabt:
    print(f', out = {i}', end='')
print('\n--\n')
print("False values (0):")
for i in tabf:
    print(f', out = {i}', end='')
