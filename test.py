a = '12d12djj22'
a = list(a)
for i in range(len(a)):
    if a[i].isalpha() == False:
        a[i] = str(0)
        
a = "".join(a)
print(a)