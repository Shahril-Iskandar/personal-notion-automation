import random
import string

def generate_random_string(length=10):
	# Get all the ASCII letters in lowercase and uppercase
	letters = string.ascii_letters
	# Randomly choose characters from letters for the given length of the string
	random_string = ''.join(random.choice(letters) for i in range(length))
	return random_string

# # Example usage: generate a random string of length 10
# random_string = generate_random_string()
# print(random_string)
