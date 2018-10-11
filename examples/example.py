import obf

o=obf.obfuscator()
print(o.encode('hello'))


list_of_words = ['hello','world,','this is', 'a test', 'world']
list_of_codewords = []
for i in list_of_words:
    print("{} -> {} ->{}".format(i,o.encode(i),o.encode_text(i)))


def encode_list(list_of_stuff_to_encode, treat_as_text=False):
    ob = obf.obfuscator()
    results =[]

    if treat_as_text:
        for i in list_of_stuff_to_encode:
            results.append(ob.encode_text(i))
    else:
        for j in list_of_stuff_to_encode:
            results.append(ob.encode(j))

    return results

print(encode_list(list_of_words,False))
print(encode_list(list_of_words,True))