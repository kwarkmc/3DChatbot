# a = '12d12dj^^j22'
# a = list(a)
# for i in range(len(a)):
#     if a[i].isalpha() == False:
#         a[i] = str(0)
        
# a = "".join(a)
# print(a)

detected = []
detected.sort(key=lambda x:x[1], reverse=True)
print(detected)