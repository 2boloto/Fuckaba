#!/usr/bin/python3

# Интерпретатор работает в дебажном режиме:
# - команда `:` печатает шестнадцатеричное представление байта в стандартный поток ошибок;
# - `~` дампит туда же память;
# - `?` завершает программу.

maximum_code_length = 2 ** 20
memory_length = 2 ** 20

def interpret(code, memory, read, write, debug = None, debug_write = None):
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

	position = 0
	instructions_count = 0

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
				last_pointer = max(last_pointer, pointer)
			elif debug is not None:
				if instruction == ":":
					debug_write(memory[pointer])
				elif instruction == "~":
					debug(position + 1, pointer, last_pointer, instructions_count)
				elif instruction == "?":
					position = len(code) - 1

			position += 1
			instructions_count += 1

	return pointer, last_pointer, instructions_count

if __name__ == "__main__":
	from sys import argv, stdin, stdout, stderr

	with open(argv[1]) as file:
		code = file.read(maximum_code_length)

		if file.read(1) != "":
			raise Exception("Слишком много кода")

	memory = bytearray(memory_length)

	def read():
		return stdin.buffer.read(1)[0]

	def write(byte):
		stdout.buffer.write(bytes([byte]))
		stdout.buffer.flush()

	def debug(position, pointer, last_pointer, instructions_count):
		dump = " ".join("{:02x}".format(memory[i]) + ("<" if i == pointer else "") for i in range(last_pointer + 1))

		stderr.write("{}\n{}\n".format(dump, "=" * 16))
		stderr.write("Позиция в коде: {}\n".format(position))
		stderr.write("Указатель: {}\n".format(pointer))
		stderr.write("Выполнено инструкций: {}\n".format(instructions_count))
		stderr.write("Использованно ячеек: {}\n\n".format(last_pointer + 1))
		stderr.flush()

	def debug_write(byte):
		stderr.write("{:02x}\n".format(byte))
		stderr.flush()

	interpret(code, memory, read, write, debug, debug_write)
