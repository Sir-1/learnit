def hash(password):
    edit = []
    edit += password
    print(edit)
    for i in range(len(edit)):
        edit[i] = str(ord(edit[i]))
    print(edit)
    password = ''.join(edit)
    print(password)
    password = int(((int(password)/10)**0.5 * int(password) % 1000.5)**5)
    return password


print(hash("1234"))
