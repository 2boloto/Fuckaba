#!/usr/bin/python3

# Интерпретатор работает в дебажном режиме: поддерживает дополнительную команду `~` для вывода байта в стандартный поток ошибок и дампит туда же память после исполнения программы.

maximum_code_length = 2 ** 20
memory_length = 2 ** 20

from sys import argv, stdin, stdout, stderr

with open(argv[1]) as file:
	code = file.read(maximum_code_length)

	if file.read(1) != "":
		raise Exception("Слишком много кода")

memory = bytearray(memory_length)

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
last_pointer = 0
i = 0

while i < len(code):
	if code[i] == "[":
		if memory[pointer] == 0:
			i = loops[i]
		else:
			stack.append(i)
			i += 1
	elif code[i] == "]":
		i = stack.pop()
	else:
		if code[i] == ",":
			memory[pointer] = stdin.buffer.read(1)[0]
		elif code[i] == ".":
			stdout.buffer.write(memory[pointer: pointer + 1])
			stdout.buffer.flush()
		elif code[i] == "~":
			stderr.buffer.write(memory[pointer: pointer + 1])
			stderr.buffer.flush()
		elif code[i] == "-":
			memory[pointer] = memory[pointer] - 1 & 0xff
		elif code[i] == "+":
			memory[pointer] = memory[pointer] + 1 & 0xff
		elif code[i] == "<":
			if pointer == 0:
				raise Exception("Слишком лево")

			pointer -= 1
		elif code[i] == ">":
			if pointer == len(memory) - 1:
				raise Exception("Слишком право")

			pointer += 1
			last_pointer = max(last_pointer, pointer)

		i += 1

stderr.write(repr(memory[: last_pointer + 1]))
