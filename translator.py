#!/usr/bin/python3

maximum_code_length = 2 ** 20
memory_length = 2 ** 20

def translate(code, memory_length, safe = True):
	result = ""

	depth = 0

	for i in code:
		if i == "]":
			if depth == 0:
				raise Exception("Неоткрытая скобка")

			result += "}"
			depth -= 1
		elif i == "[":
			result += "while (*p != 0) {"
			depth += 1
		elif i == ",":
			result += "if (!read(p)) return false;"
		elif i == ".":
			result += "if (!write(p)) return false;"
		elif i == "-":
			result += "*p = *p + 255 & 0xff;"
		elif i == "+":
			result += "*p = *p + 1 & 0xff;"
		elif i == "<":
			if safe:
				result += "if (p == memory) return false;"

			result += "--p;"
		elif i == ">":
			if safe:
				result += "if (p == memory + MEMORY_LENGTH - 1) return false;"

			result += "++p;"

	if depth != 0:
		raise Exception("Незакрытая скобка")

	return """
		#include <stdlib.h>
		#include <stdint.h>
		#include <stdbool.h>

		#define MEMORY_LENGTH {}

		static uint8_t memory[MEMORY_LENGTH];

		static bool execute(bool (*read)(uint8_t *cell), bool (*write)(const uint8_t *cell)) {{
			uint8_t *p = memory;

			{}

			return true;
		}}
	""".format(memory_length, result)

def stdio():
	return """
		#include <stdio.h>

		static bool read(uint8_t *cell) {
			int character = getchar();

			if (character == EOF) {
				return false;
			} else {
				*cell = character;

				return true;
			}
		}

		static bool write(const uint8_t *cell) {
			bool result = putchar(*cell) == EOF ? false : true;

			if (result) {
				result = fflush(stdout) == EOF ? false : true;
			}

			return result;
		}
	"""

def run():
	return """
		int main(void) {
			freopen(NULL, "rb", stdin);

			return execute(read, write) == true ? EXIT_SUCCESS : EXIT_FAILURE;
		}
	"""

if __name__ == "__main__":
	import sys

	with open(sys.argv[1]) as file:
		code = file.read(maximum_code_length)

		if file.read(1) != "":
			raise Exception("Слишком много кода")

	print(translate(code, memory_length) + stdio() + run())
