#!/usr/bin/python3

maximum_code_length = 2 ** 20
memory_length = 363 * 2 ** 20

def interpret(code, memory, read, write):
	loops = {}
	stack = []

	for i in range(len(code)):
		if code[i] == "[":
			stack.append(i)
		elif code[i] == "]":
			loops[stack.pop()] = i + 1

	if len(stack) != 0:
		raise Exception("Незакрытая скобка")

	pointer = 0
	position = 0

	while position < len(code):
		instruction = code[position]

		if instruction == "[":
			if memory[pointer] == 0:
				position = loops[position]
			else:
				stack.append(position)
				position += 1
		elif instruction == "]":
			position = stack.pop()
		else:
			if instruction == ",":
				memory[pointer] = read()
			elif instruction == ".":
				write(memory[pointer])
			elif instruction == "-":
				memory[pointer] = memory[pointer] - 1 & 0xff
			elif instruction == "+":
				memory[pointer] = memory[pointer] + 1 & 0xff
			elif instruction == "<":
				if pointer == 0:
					raise Exception("Слишком лево")

				pointer -= 1
			elif instruction == ">":
				if pointer == len(memory) - 1:
					raise Exception("Слишком право")

				pointer += 1

			position += 1

	return pointer

if __name__ == "__main__":
	import sys

	with open(sys.argv[1]) as file:
		code = file.read(maximum_code_length)

		if file.read(1) != "":
			raise Exception("Слишком много кода")

	def read():
		return sys.stdin.buffer.read(1)[0]

	def write(byte):
		sys.stdout.buffer.write(bytes([byte]))
		sys.stdout.flush()

	interpret(code, bytearray(memory_length), read, write)
