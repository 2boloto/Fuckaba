#!/usr/bin/python3

commands = {}

def command(function):
	commands[function.__name__[: -8].upper()] = function

	return function

@command
def go_command(count):
	count = int(count)

	if count > 0:
		return ">" * count
	else:
		return "<" * -count

def repeat(instruction, count):
	if count > 0:
		result = ">".join(instruction * count)
	else:
		result = "<".join(instruction * -count)

	result += go_command(-(count - 1)) if count != 0 else ""

	return result

@command
def input_command(count):
	return repeat(",", int(count))

@command
def output_command(count):
	return repeat(".", int(count))

@command
def zero_command():
	return "[-]"

@command
def add_command(number):
	number = int(number)

	if number > 0:
		return "+" * number
	else:
		return "-" * -number

@command
def not_command():
	return ">+<[[-]>-<]>[-<+>]<"

@command
def if_command():
	return "["

@command
def endif_command():
	return "[-]]"

import os.path
import json

def preprocess(code, root = "."):
	result = ""

	for i in code.split("\n"):
		i = i.strip().split("//")[0]

		if i.startswith("#"):
			name, *arguments = i[1: ].split()

			if name == "IMPORT":
				path = json.loads(arguments[0])

				if type(path) is not str or len(arguments) != 1:
					raise Exception("Wrong import arguments")

				with open(os.path.join(root, path)) as file:
					imported = file.read()

				result += preprocess(imported, os.path.split(path)[0])
			elif name in commands:
				result += commands[name](*arguments)
			else:
				raise Exception("Unknown command")
		else:
			result += i

	return result

def compress(code):
	result = ""

	for i in code:
		if i in "[],.-+><":
			result += i

	return result

import sys

sys.stdout.write("#!interpreter\n" + compress(preprocess(sys.stdin.read())))
