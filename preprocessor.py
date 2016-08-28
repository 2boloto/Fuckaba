#!/usr/bin/python3

commands = {}

def command(function):
	commands[function.__name__[: -8].upper()] = function

	return function

# Простые команды

@command
def go_command(count):
	"Переходит на задданой число ячеек влево или вправо"

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
def inc_command(number):
	"Увеличивает или уменьшает данную ячеку на заданное число"

	number = int(number)

	if number > 0:
		return "+" * number
	else:
		return "-" * -number

@command
def if_command():
	return "["

@command
def endif_command():
	return "[-]]"

@command
def for_command():
	return "["

@command
def endfor_command():
	return "-]"

@command
def while_command():
	return "["

@command
def endwhile_command():
	return "]"

# Команды с несколькими вводами

@command
def copy_command():
	"""
		Копирует данную ячейку в соседнюю.

		> a
		> 0
		> 0

		< a
		< a
		< 0
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
	"Принимает соединение"

	return output_command(1)

@command
def network_recv_command():
	"""
		Принимает данные.

		> l - требуемая длина данных
		> 0

		< r - длина полученных данных, может быть меньше требуемой
		< 0

		После этого надо прочитать r байтов - это сами данные.
	"""

	return (
		go_command(1) + inc_command(1) + output_command(1) + inc_command(-1) + go_command(-1) +
		output_command(1) + input_command(1)
	)

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

	return (
		go_command(1) + inc_command(2) + output_command(1) + inc_command(-2) + go_command(-1) +
		output_command(1)
	)

@command
def network_close_command():
	"Закрывает соединение"

	return inc_command(3) + output_command(1)

import os.path
import json

def preprocess(code, root = "."):
	result = ""

	for i in code.split("\n"):
		i = i.strip().split("//")[0]

		if i.startswith("#"):
			name, *arguments = i[1: ].split()

			if name == "INCLUDE":
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
