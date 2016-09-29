#!/usr/bin/python3

import sys

import translator
import interpreter

with open(sys.argv[1], "rb") as file:
	initialized_memory = translator.load_state(file)[2]

with open(sys.argv[2], "r") as file:
	new_code = file.read()

def search_database(memory, pointer, check = False):
	keep = True

	while keep:
		if check and memory[pointer + 39: pointer + 42] != b"\x00\x00\x00":
			break

		if memory[pointer + 36] == 0:
			keep = False

		pointer += 48
	else:
		return pointer, False

	return pointer, True

new_position = new_code.index("&")
new_memory = bytearray(interpreter.memory_length)
new_pointer = interpreter.interpret(new_code[: new_position], new_memory)

start = search_database(initialized_memory, 5)[0]
start, result = search_database(initialized_memory, start, True)

if result:
	end = search_database(initialized_memory, start)[0]

	posts = b"\x00\x00\x00\x00\x00" + initialized_memory[start: end - 5]
	posts += b"\x00" * (end - start - len(posts))

	new_memory[new_pointer - 7] = 1
	new_memory[new_pointer: new_pointer + len(posts)] = posts
	new_pointer += len(posts)

with open(sys.argv[3], "wb") as file:
	translator.save_state(file, new_code, new_position, new_memory, new_pointer)
