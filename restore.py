#!/usr/bin/python3

import sys
import os

with open(sys.argv[1]) as file:
	position, pointer = map(int, file)

position = 1

if len(sys.argv) == 4:
	import interpreter

	with open(sys.argv[3]) as file:
		instructions, loops, IO = interpreter.parse(file, os.stat(sys.argv[3]).st_size)

	with open(sys.argv[2], "r+b") as file:
		posts = []

		for i in range(pointer - 43, -1, -48):
			file.seek(i)
			chunk = file.read(48)

			if chunk[-9: -6] == b"\x00\x00\x00":
				break

			posts.append(chunk)

		posts.reverse()

		memory = bytearray(os.stat(sys.argv[2]).st_size)
		pointer = interpreter.interpret(instructions[: instructions.index("W")], loops, memory)

		file.seek(0)
		file.write(memory[: pointer - 7])
		file.write(b"\x01\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00")

		for i in posts:
			file.write(i)

		pointer += len(posts) * 48

with open(sys.argv[1], "w") as file:
	file.write("{}\n{}\n".format(position, pointer))
