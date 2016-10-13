#!/usr/bin/python3

import string

execute_template = string.Template("""
	#include <string.h>
	#include <stdint.h>
	#include <stdbool.h>

	#define MEMORY_LENGTH $memory_length

	static const char code[] = {$code};
	static const uint8_t initialized_memory[] = {$initialized_memory};

	static uintptr_t position;
	static uint8_t memory[MEMORY_LENGTH];
	static uint8_t *pointer = memory + $pointer;

	static bool execute(bool (*read)(uint8_t *cell), bool (*write)(const uint8_t *cell)) {
		memcpy(memory, initialized_memory, sizeof initialized_memory);

		goto start;

		$instructions

		return true;
	}
""")

main_template = string.Template("""
	#include <stdio.h>
	#include <stdlib.h>
	#include <errno.h>
	#include <stdbool.h>
	#include <inttypes.h>

	#include <unistd.h>
	#include <sys/syscall.h>
	#include <sys/prctl.h>
	#include <linux/seccomp.h>

	static bool read_cell(uint8_t *cell) {
		while (true) {
			ssize_t result = syscall(SYS_read, 0, cell, 1);

			if (result == 1) {
				return true;
			} else if (result != EINTR) {
				return false;
			}
		}
	}

	static bool write_cell(const uint8_t *cell) {
		while (true) {
			ssize_t result = syscall(SYS_write, 1, cell, 1);

			if (result == 1) {
				return true;
			} else if (result != EINTR) {
				return false;
			}
		}
	}

	int main(void) {
		freopen(NULL, "rb", stdin);
		fclose(stderr);

		if (syscall(SYS_prctl, PR_SET_SECCOMP, SECCOMP_MODE_STRICT) != 0) {
			return EXIT_FAILURE;
		}

		syscall(SYS_exit, execute(read_cell, write_cell) == true ? EXIT_SUCCESS : EXIT_FAILURE);
	}

	static size_t nonzero_memory_length(void) {
		size_t result = 0;

		for (size_t i = MEMORY_LENGTH; i-- > 0; ){
			if (memory[i] != 0) {
				result = i + 1;
				break;
			}
		}

		return result;
	}
""")

import itertools

def translate(maximum_loop_depth, code, memory_length, initialized_memory, position = 0, pointer = 0, safe = True):
	instructions = ""

	depth = 0

	for instruction, i in zip(code, itertools.count()):
		if i == position:
			instructions += "start:"
			position = None

		if instruction == "]":
			if depth == 0:
				raise Exception("Неоткрытая скобка")

			instructions += "}"
			depth -= 1
		elif instruction == "[":
			instructions += "while (*pointer != 0) {"
			depth += 1

			if depth > maximum_loop_depth:
				raise Exception("Слишком глубокая вложенность")
		elif instruction == ",":
			instructions += "position = {}; if (!read(pointer)) {{return false;}}".format(i)
		elif instruction == ".":
			instructions += "position = {}; if (!write(pointer)) {{return false;}}".format(i)
		elif instruction == "-":
			instructions += "*pointer = *pointer + 255 & 0xff;"
		elif instruction == "+":
			instructions += "*pointer = *pointer + 1 & 0xff;"
		elif instruction == "<":
			if safe:
				instructions += "if (pointer == memory) {return false;}"

			instructions += "--pointer;"
		elif instruction == ">":
			if safe:
				instructions += "if (pointer == memory + MEMORY_LENGTH - 1) {return false;}"

			instructions += "++pointer;"

	if position is not None:
		result += "start:"

	if depth != 0:
		raise Exception("Незакрытая скобка")

	return execute_template.substitute(
		code = ", ".join("0x{:02x}".format(i) for i in code.encode()),
		memory_length = memory_length,
		initialized_memory = ", ".join("0x{:02x}".format(i) for i in initialized_memory),
		pointer = pointer,
		instructions = instructions
	)

def create_main():
	return main_template.substitute()

def load_state(file, maximum_code_length = None, memory_length = None):
	position, pointer, code_length, initialized_memory_length = map(int, file.readline().split())

	if (
		position < 0 or position >= code_length or
		pointer < 0 or
		code_length < 0 or
		initialized_memory_length < 0
	):
		raise Exception("Неправильный формат")

	position += 1

	if memory_length is not None:
		if pointer > memory_length:
			raise Exception("Слишком большой указатель")

		if initialized_memory_length > memory_length:
			raise Exception("Слишком много начальной памяти")

	if maximum_code_length is not None:
		if code_length > maximum_code_length:
			raise Exception("Слишком много кода")

	code = file.read(code_length)

	if len(code) < code_length:
		raise Exception("Неправильный формат")

	code = code.decode()
	initialized_memory = file.read(initialized_memory_length)

	if len(initialized_memory) != initialized_memory_length:
		raise Exception("Неправильный формат")

	if file.read(1) != b"":
		raise Exception("Неправильный формат")

	return code, position, initialized_memory, pointer

def save_state(file, code, position, memory, pointer):
	code = code.encode()

	initialized_memory_length = 0

	for i in range(len(memory) - 1, -1, -1):
		if memory[i] != 0:
			initialized_memory_length = i + 1

			break

	file.write("{} {} {} {}\n".format(position, pointer, len(code), initialized_memory_length).encode())
	file.write(code)
	file.write(memory[: initialized_memory_length])
	file.flush()

if __name__ == "__main__":
	import argparse
	import sys

	import interpreter

	parser = argparse.ArgumentParser()

	parser.add_argument("--maximum-code-length", "-c", type = int, default = 2 ** 20)
	parser.add_argument("--maximum-loop-depth", "-w", type = int, default = 256)
	parser.add_argument("input", type = str)
	parser.add_argument("--position", "-i", type = int, default = 0)
	parser.add_argument("--memory-length", "-l", type = int, default = interpreter.memory_length)
	parser.add_argument("--memory", "-m", type = str)
	parser.add_argument("--pointer", "-p", type = int, default = 0)
	parser.add_argument("--state", "-s", action = "store_true")

	arguments = parser.parse_args()

	maximum_code_length = arguments.maximum_code_length
	maximum_loop_depth = arguments.maximum_loop_depth
	memory_length = arguments.memory_length

	if arguments.state:
		with open(arguments.input, "rb") as file:
			code, position, initialized_memory, pointer = load_state(file, maximum_code_length, memory_length)
	else:
		position = arguments.position
		initialized_memory = b""
		pointer = arguments.pointer

		with open(arguments.input, "r") as file:
			code = file.read(maximum_code_length)

			if file.read(1) != "":
				raise Exception("Слишком много кода")

		if arguments.memory is not None:
			with open(arguments.memory, "rb") as file:
				initialized_memory = file.read()

				if file.read(1) != b"":
					raise Exception("Слишком много начальной памяти")

	sys.stdout.write(
		translate(maximum_loop_depth, code, memory_length, initialized_memory, position, pointer) +
		create_main()
	)
