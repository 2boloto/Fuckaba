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
	#include <signal.h>
	#include <stdbool.h>
	#include <inttypes.h>

	sig_atomic_t signaled;

	static void dump(void) {
		FILE *file = fopen((const char []) {$dump_filename}, "wb");

		size_t initialized_memory_length = 0;

		if (file != NULL) {
			for (size_t i = MEMORY_LENGTH; i-- > 0; ){
				if (memory[i] != 0) {
					initialized_memory_length = i + 1;

					break;
				}
			}

			fprintf(file, "%" PRIuPTR " %tu %zu %zu\\n", position, pointer - memory, sizeof code, initialized_memory_length);
			fwrite(code, sizeof code, sizeof *code, file);
			fwrite(memory, initialized_memory_length, sizeof *code, file);
			fflush(file);
		}
	}

	static bool read(uint8_t *cell) {
		int character = getchar();

		if (character == EOF) {
			return false;
		} else {
			*cell = character;

			if (signaled != 0) {
				dump();

				signaled = 0;
			}

			return true;
		}
	}

	static bool write(const uint8_t *cell) {
		putchar(*cell);
		fflush(stdout);

		if (ferror(stdout) != 0) {
			return false;
		} else {
			if (signaled != 0) {
				dump();

				signaled = 0;
			}

			return true;
		}
	}

	static void handler(int number) {
		signaled = 1;
	}

	int main(void) {
		freopen(NULL, "rb", stdin);

		struct sigaction action = {
			.sa_handler = handler,
			.sa_flags = SA_RESTART
		};

		sigemptyset(&action.sa_mask);
		sigaction(SIGUSR1, &action, NULL);

		return execute(read, write) == true ? EXIT_SUCCESS : EXIT_FAILURE;
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

def create_main(dump_filename):
	return main_template.substitute(
		dump_filename = ", ".join("0x{:02x}".format(i) for i in dump_filename.encode() + b"\x00")
	)

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
	parser.add_argument("--dump", "-d", type = str, default = "dump.bin")
	parser.add_argument("--state", "-s", action = "store_true")

	arguments = parser.parse_args()

	maximum_code_length = arguments.maximum_code_length
	maximum_loop_depth = arguments.maximum_loop_depth
	memory_length = arguments.memory_length
	dump_filename = arguments.dump

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
		create_main(dump_filename)
	)
