#!/usr/bin/python3

commands = {}

def command(function):
	commands[function.__name__[: -8].upper()] = function

	return function

# Простые команды

def move(count):
	if count > 0:
		return ">" * count
	else:
		return "<" * -count

def increment(count):
	if count > 0:
		return "+" * count
	else:
		return "-" * -count

def repeat(instruction, count):
	if count > 0:
		result = ">".join(instruction * count)
	else:
		result = "<".join(instruction * -count)

	result += move(-(count - 1)) if count != 0 else ""

	return result

@command
def go_command(count):
	"Переходит на задданой число ячеек влево или вправо"

	return move(int(count))

@command
def input_command(count):
	"Вводит заданное число байтов, заполняя ячейки, начиная с текущей. Если число отрицательное, заполняет влево"

	return repeat(",", int(count))

@command
def output_command(count):
	"Выводит заданное число байтов из ячеек, начиная с текущей. Если число отрицательное, читает влево"

	return repeat(".", int(count))

@command
def zero_command():
	"Зануляет данную ячейку"

	return "[-]"

@command
def inc_command(count):
	"Увеличивает или уменьшает данную ячеку на заданное число"

	return increment(int(count))

# Команды с несколькими вводами

@command
def copy_command():
	"""
		Складывает данную ячейку с соседней и второй справа.

		> a
		> b
		> c

		< a + c
		< b + a
		< 0

		Если b и c - нули, то происходит просто копирование.
	"""

	return "[->+>+<<]>>[-<<+>>]<<"

@command
def add_command():
	"""
		Складывает данную ячеку с соседней.

		> a
		> b

		< 0
		< a + b
	"""

	return "[->+<]"

@command
def sub_command():
	"""
		Отнимает данную ячеку от соседней.

		> a
		> b

		< 0
		< b - a
	"""

	return "[->-<]"

@command
def subsat_command():
	"""
		Отнимает с насыщением данную ячеку от второй справа. То есть если a > b, то получается их разность, а иначе 0.

		> a
		> 0
		> b

		< 0
		< 0
		< b - a, если b > 0, иначе 0
	"""

	return "[>>[-<]<[>]<-]"

@command
def not_command():
	"""
		Обаращает значение данной ячейки.

		> a
		> 0

		< !a
		< 0
	"""

	return ">+<[[-]>-<]>[-<+>]<"

@command
def test_shift_command(shift, value):
	"""
		Проверяет указанную ячейку на равенство указанному значению.

		> a
		> ...
		> b

		< a + 1, если неравно, a, если равно
		< ...
		< 0
	"""

	shift = int(shift)

	return (
		move(shift) + increment(-int(value)) + "[" +
		move(-shift) + "+" + move(shift) +
		"[-]]" + move(-shift)
	)

# Массив

"""
	Это структура данных:

	0
	0

	За которыми следуют элементы:

	1
	d - байт данных

	А за ними ещё:

	0
	0

	Например:

	0
	0
	1
	63
	1
	33
	0
	0

	Такую структуру удобно дополнять: с помощью цикла можно проехаться до конца массива и дописать ещё элемент. Или удалить последний.
"""

@command
def array_end_command():
	"Перемещается в конец массива"

	return ">>[>>]"

@command
def array_start_command():
	"Перемещается в начало массива"

	return "[<<]"

@command
def array_append_command():
	"Добавляет нулевой элемент в массив. Предполагается, что после массива есть два нуля"

	return "+"

@command
def array_pop_command():
	"Удаляет элемент из массива"

	return "<[-]<-"

# Сетевые команды

@command
def network_accept_command():
	"""
		Принимает соединение.

		> 0

		< 0
	"""

	return "."

@command
def network_recv_command():
	"""
		Принимает данные.

		> l - требуемая длина данных
		> 0

		< r - длина полученных данных, может быть меньше требуемой. Если 0, то соединение прервалось
		< 0

		После этого надо прочитать r байтов - это сами данные.
	"""

	return ">+.-<.,"

@command
def network_send_command():
	"""
		Отправляет данные.

		> l - длина
		> 0

		< l
		< 0

		После этого надо вывести l байтов и прочитать 1 - длину действительно отправленного, она может быть меньше l.
	"""

	return ">++.--<."

@command
def network_close_command():
	"""
		Закрывает соединение.

		> 0

		< 0
	"""

	return "+++.---"

# Особые команды

def include_command(root, path):
	path = json.loads(path)

	with open(os.path.join(root, path)) as file:
		imported = file.read()

	return preprocess(imported, os.path.split(path)[0])

blocks = {
	"BLOCK": ("", ""),
	"IF": ("[", "[-]]"),
	"FOR": ("[", "-]"),
	"WHILE": ("[", "]")
}

def start_block_command(stack, block, shift):
	stack.append((block[1], shift))

	return block[0]

def end_block_command(stack, shift):
	if shift is not None:
		raise Exception("Сдвиг у конца блока")

	return stack.pop()

import os.path
import json

def preprocess(code, root = "."):
	result = ""

	stack = []

	for i in code.split("\n"):
		i = i.strip().split("//")[0]

		if i.startswith("#"):
			name, *arguments = i[1: ].split()

			if len(arguments) > 0 and arguments[-1].startswith("<>"):
				shift = int(arguments.pop()[2: ])

				result += move(shift)
			else:
				shift = None

			if name == "INCLUDE":
				result += include_command(root, *arguments)
			elif name in blocks:
				result += start_block_command(stack, blocks[name], shift, *arguments)
				shift = None
			elif name == "END":
				code, shift = end_block_command(stack, shift, *arguments)
				result += code
			elif name in commands:
				result += commands[name](*arguments)
			else:
				raise Exception("Неизвестная команда")

			if shift is not None:
				result += move(-shift)
		else:
			result += i

	if len(stack) != 0:
		raise Exception("Не хватает `END`")

	return result

def compress(code):
	result = ""

	def reorder(code):
		shift = 0
		differences = {}

		for i in code:
			if i == "-":
				differences[shift] = differences.get(shift, 0) - 1
			elif i == "+":
				differences[shift] = differences.get(shift, 0) + 1
			elif i == "<":
				shift -= 1
			else:
				shift += 1

		left_moves = list(sorted((i for i in differences if i < 0), reverse = True))
		right_moves = list(sorted(i for i in differences if i >= 0))

		result = ""
		pointer = 0

		def encode(moves):
			nonlocal result, pointer

			for i in moves:
				difference = differences[i] % 256

				result += move(i - pointer)
				result += increment(difference if difference <= 128 else -(256 - difference))
				pointer = i

		if shift > 0:
			encode(left_moves)
			encode(right_moves)
		else:
			encode(right_moves)
			encode(left_moves)

		result += move(shift - pointer)
		pointer = shift

		return result

	fragment = ""

	for i in code:
		if i in "-+><":
			fragment += i
		elif i in "[],.":
			result += reorder(fragment) + i
			fragment = ""

	return result

import sys

sys.stdout.write("#!interpreter\n" + compress(preprocess(sys.stdin.read())))
