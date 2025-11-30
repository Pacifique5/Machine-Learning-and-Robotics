# text = '''This is an example of a string
# that contains triple single quotes.'''
# print(text)

# x=str(3)
# y=int(3)
# z=float(3)

# print(x)
# print(y)
# print(z)

 
# x = 5
# y = "John"
# print(type(x))
# print(type(y))

# age, weight, names= 10, 25.5, "John Kagabo",
# print(age)
# print(weight)
# print(names)

# x=2,3,4
# print(x)

# fruits = ("apple", "banana", "cherry", "strawberry", "raspberry")
# (green, yellow, *red) = fruits
# print(green)
# print(yellow)
# print(red)

# fruits = ("apple", "banana", "cherry", "strawberry", "raspberry")
# (green, yellow, red) = fruits
# print(green)
# print(yellow)
# print(red)

# x = "awesome"
# def myfunc():
#     x = "fantastic"
#     print("Python is " + x)

#     myfunc()

#     print("Python is " + x)

# def myfunc():
#     global x
#     x = "fantastic"

#     myfunc()
#     print("Python is " + x)

# name = "Mugisha Pacifique"
# name_bytes = name.encode("utf-8")
# print(name_bytes)

# decoded_name = name_bytes.decode("utf-8")
# print(decoded_name)

# byte_range = bytes(range(91, 100))
# print(byte_range)

# decoded = byte_range.decode("utf-8", errors="replace")
# print(decoded)

# ...existing code...

# name = "John Kagabo"

# encoded_bytes = bytes([ord(char) + 91 for char in name])
# print("Encoded bytes:", encoded_bytes)

# decoded_name = ''.join([chr(byte - 91) for byte in encoded_bytes])
# print("Decoded name:", decoded_name)

# x = 1
# y = 2.8
# z = 1j

# real_part = z.real
# imaginary_part = z.imag

# print("Real part:", real_part)
# print("Imaginary part:", imaginary_part)


# import random
#  print(random.randrange(1, 10))

# b = "Pacifique"
# print(b[2:5])
# print(b[-5:-2])

# name = "Hello, here"
# '''
# str_var_name[start:stop:step].
# When:
# start is omitted (default 0).
# stop is omitted (default is the length of the string).
# step is omitted (default 1).
# '''
# print(name[::-2])

# age = 18
# message = f"You are {'eligible' if age >= 18 else 'not eligible'} to vote."
# print(message)

# def my_converter(x):
#     return x*0.3048

# txt = f"A plane can flying at a {my_converter(333333):,.2f} meter altitude."
# print(txt)

# txt1 = "My name is {fname}, I'm {age}". format(fname = "John", age = 36)
# txt2 = "My name is {0}, I'm {1}".format("John", 36)
# txt3 = "My name is {}, I'm {}".format("John", 36)

# txt = "hello world.".capitalize()
# txt = "hello world.".casefold()
# txt = "Hello World".center(30)

# text = "hello world"

# # find()
# print(text.find("world"))   # Output: 6
# print(text.find("Python"))  # Output: -1

# # index()
# print(text.index("world"))  # Output: 6
# # print(text.index("Python"))  # Raises ValueError

# text = "   hello world   "
# stripped_text = text.strip()
# print(stripped_text)  # Output: 'hello world'

# thislist = ["apple", "banana", "cherry", "orange", "kiwi", "mango", "melon"]
# print(thislist[2:5])

# thislist = ["apple", "banana", "cherry", "orange", "kiwi", "mango", "melon"]
# print(thislist[1], ["banana"])

# thislist = ["apple", "banana", "cherry"]
# thislist[1:2]
# # thislist[1]
# print(thislist)

# # ...existing code...

# thislist = ["apple", "banana", "cherry"]
# # thislist[1] = "orange" 
# thislist[1:2] = "orange" 
# print(thislist)        

# Create a list of 10 items
# my_list = ["apple", "banana", "cherry", "orange", "kiwi", "mango", "melon", "pear", "grape", "plum"]

# # Access one item using index
# print(my_list[3])  # Output: orange

# # Access multiple items using slice
# print(my_list[2:6])  # Output: ['cherry', 'orange', 'kiwi', 'mango']

# fruits = ["apple", "banana" , "cherry"]
# more_fruits = ["orange" , "kiwi", "mango"]
# fruits.extend(more_fruits)
# # fruits.pop(0)
# print(fruits)

# fruits = ["apple"]
# fruits.extend(["attend"])
# print(fruits)

# thislist = ["apple", "banana", "cherry"]
# thislist[1] = "blackcurrant"
# thislist[1] = ["blackcurrant", "watermelom"]
# thislist[1:2] = ["blackcurrant"]
# print(thislist)

# thislist = ["apple", "banana", "cherry"]
# thislist.insert(1, "watermelon")
# print(thislist) 

# thislist = ["apple", "banana", "cherry"]
# [print (x) for x in thislist]

# thislist = ["apple", "banana", "cherry"]
# i = 0;
# while i < len(thislist):
#     print(thislist[i])
#     i = i + 1

# def count_vowels(word):
#     return sum(1 for char in word.lower() if char in "aeiou")

# thislist = ["orange", "mango", "kiwi", "pineapple", "banana"]
# thislist.sort(key=count_vowels)
# print(thislist)

# def greet(name):
#     return f"Hello, {name}!"

# message = greet("fique")
# print(message)

# def my_function(*ars):
#     return ars

# print(my_function("Mike", 10, True, [1, 2, 3], {"name": "fique"}))

def get_fruits(**fruits):
    print("The sweetest fruit is " + fruits["fruit3"])

    get_fruits(fruit1 = "apple", fruit2="banana", fruit3="mango")
    