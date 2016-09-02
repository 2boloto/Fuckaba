#!/usr/bin/python3

# В комментах к командам символом `>` обозначается состояние памяти перед вызовом, а `<` - после
# Дефисом после треугольной скобки обозначено положение указателя

import os.path

names = {"END"}
commands = {}
blocks = {}

def command(function):
	name = function.__name__[: -8].upper()

	if name in names:
		raise Exception("Имя занято")

	commands[name] = function
	names.add(name)

	return function

def block(function):
	name = function.__name__[: -6].upper()

	if name in names:
		raise Exception("Имя занято")

	blocks[name] = function
	names.add(name)

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

@command
def go_command(count):
	"Переходит на задданой число ячеек влево или вправо"

	return move(count)

@command
def input_command():
	"Вводит байт"

	return ","

@command
def output_command():
	"Выводит байт"

	return "."

@command
def zero_command():
	"Зануляет данную ячейку"

	return "[-]"

@command
def inc_command(count):
	"Увеличивает или уменьшает данную ячеку на заданное число"

	return increment(count)

@command
def include_command(path):
	"Вставляет код из другого файла, обработав его препроцессором"

	global root

	path = os.path.join(root, path)

	with open(path) as file:
		code = file.read()

	temp = root
	root = os.path.split(path)[0]
	result = preprocess_part(code)
	root = temp

	return result

@block
def block_block():
	"Блок кода"

	return "", ""

@block
def if_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. После выполнения она зануляется.

		>- a

		<- a

		>- неважно

		<- 0
	"""

	return "[", "[-]]"

@block
def bool_if_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. После выполнения она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 1

		>- 1

		<- 0
	"""

	return "[", "-]"

@block
def if_l_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Перед выполненем она зануляется.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "[[-]", "]"

@block
def bool_if_l_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Перед выполнения она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "[-", "]"

@block
def if_save_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется.

		>- a
		>  0
		>  0

		<- a
		<  0
		<  0

		>- x - неважно
		>  0
		>  0

		<- a, если не выполнился, иначе x
		<  0
		<  0
	"""

	return "[", ">>+<]>[-<]<"

@block
def if_save_flag_block():
	"""
		Условный блок, выполняется, если данная ячейка - не нуль. Её значение сохраняется. Сохраняет флаг во второй справа ячейке.

		>- a
		>  0
		>  0

		<- a
		<  0
		<  0

		>- x - неважно
		>  0
		>  0

		<- a, если не выполнился, иначе x
		<  0
		<  1, если выполнился, иначе 0
	"""

	return "[", ">>+<]>[<]<"

@block
def unless_block():
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Если нет, то она зануляется.

		>- a
		>  0

		<- 0
		<  0

		>- x - неважно
		>  0

		<- 0, если не выполнился, иначе x
		<  0
	"""

	return "[[-]>+<]>-[+<", ">]<"

@block
def bool_unless_block():
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Если нет, то она зануляется.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>- a

		<- 0

		>- 0

		<- 0
	"""

	return "-[+", "]"

@block
def unless_save_block():
	"""
		Условный блок, выполняется, если данная ячейка - нуль. Её значение сохраняется.

		>- a
		>  0
		>  0

		<- 0
		<  0
		<  0

		>- x - неважно
		>  y - неважно
		>  0

		<- a, если не выолнился, иначе x
		<  0, если не выполнился, иначе y
		<  0
	"""

	return "[>>+<]>[<]>-[+<<", ">>]<<"

@block
def for_block():
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём. После каждой итерации она уменьшается на 1.

		>- a

		<- a

		>- x - неважно

		<- 0
	"""

	return "[", "-]"

@block
def for_l_block():
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём. Перед каждой итерацией она уменьшается на 1.

		>- a

		<- a - 1, если первая итерация, иначе x - 1

		>- x - неважно

		<- 0
	"""

	return "[-", "]"

@block
def while_block():
	"""
		Цикл до тех пор, пока данная ячейка не станет нулём.

		>- a

		<- a, если первая итерация, иначе x

		>- x - неважно

		<- 0
	"""

	return "[", "]"

@block
def forever_block():
	"""
		Бесконечный цикл.

		>- 0

		<- 0

		>- 0

		<- 0
	"""

	return "+[-", "+]"

# Команды с несколькими вводами

@command
def add_to_command(destination):
	"""
		Складывает данную ячейку с указанной.

		>- a
		>  ...
		>  b

		<- 0
		<  ...
		<  b + a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[-" + move(destination) + "+" + move(-destination) + "]"

@command
def sub_to_command(destination):
	"""
		Отнимает данную ячейку от указанной.

		>- a
		>  ...
		>  b

		<- 0
		<  ...
		<  b - a

		Сдвиг может быть любым, но не нулевым.
	"""

	return "[-" + move(destination) + "-" + move(-destination) + "]"

@command
def add_save_to_command(destination, buffer = 1):
	"""
		Складывает с указанной ячейкой данную, сохраняя её значение с помощью временной.

		>- a
		>  ...
		>  b
		>  ...
		>  0

		<- a
		<  ...
		<  b + a
		<  ...
		<  0

		Сдвиги не должны быть нулевыми или одинаковыми.
	"""

	return (
		"[-" + move(buffer) + "+" + move(-buffer + destination) + "+" + move(-destination) +"]" +
		move(buffer) + "[-" + move(-buffer) + "+" + move(buffer) + "]" + move(-buffer)
	)

@command
def sub_save_to_command(destination, buffer = 1):
	"""
		Отнимает от указанной ячейки данную, сохраняя её значение с помощью временной.

		>- a
		>  ...
		>  b
		>  ...
		>  0

		<- a
		<  ...
		<  b - a
		<  ...
		<  0

		Сдвиги не должны быть нулевыми или одинаковыми.
	"""

	return (
		"[-" + move(buffer) + "+" + move(-buffer + destination) + "-" + move(-destination) +"]" +
		move(buffer) + "[-" + move(-buffer) + "+" + move(buffer) + "]" + move(-buffer)
	)

@command
def not_to_command(destination):
	"""
		Обаращает значение данной ячейки.

		>  a
		>  ...
		>- 0

		<  0
		<  ...
		<- !a

		Сдвиг может быть любым, но не нулевым.
	"""

	return move(destination) + "+" + move(-destination) + "[[-]" + move(destination) + "-" + move(-destination) + "]"

@command
def bool_not_to_command(destination):
	"""
		Обаращает значение данной ячейки.

		Подразумевается, что она может принимать только два значения: 0 и 1.

		>  a
		>  ...
		>- 0

		<  0
		<  ...
		<- !a

		Сдвиг может быть любым, но не нулевым.
	"""

	return move(destination) + "+" + move(-destination) + "[-" + move(destination) + "-" + move(-destination) + "]"

# Сетевые команды

@command
def network_accept_command():
	"""
		Принимает соединение.

		>- 0

		<- 0, если успешно, иначе 1
	"""

	return ".,"

@command
def network_recv_command():
	"""
		Принимает данные.

		>- l - требуемая длина данных
		>  0

		<- 0, если успешно, иначе 1
		<  0

		Если вызов успешен, после него надо прочитать 1 байт длины и сами данные. Если длина будет 0, то соединение больше ничего не пошлёт.
	"""

	return ">+.-<.,"

@command
def network_send_command():
	"""
		Отправляет данные.

		>- l - длина
		>  0

		<- l
		<  0

		После этого надо вывести l байтов и прочитать 1 байт результата: 0, если успешно, иначе 1. В случае успеха надо прочитать ещё один байт - длину отправленного, она может быть меньше l.
	"""

	return ">++.--<."

@command
def network_close_command():
	"""
		Закрывает соединение.

		>- 0

		<- 0
	"""

	return "+++.---"

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
def array_go_end_command():
	"Перемещается в конец массива"

	return ">>[>>]"

@command
def array_go_start_command():
	"Перемещается в начало массива"

	return "<<[<<]"

@command
def array_set_command(string):
	"Создаёт массив из указанных байтов. Указатель остаётся на начале"

	base = list(sorted(string))[len(string) // 2]

	return (
		">>" + "+>>" * len(string) + ">" + increment(base) + "[-<<<[>+<<<]>>[>>]>]" +
		"<<" + "<<".join(increment(i - base) for i in reversed(string)) + "<<<"
	)

@command
def array_clear_command():
	"Очищает массив"

	return ">>[>>]<<[->[-]<<<]"

@command
def array_compare_command(string):
	"""
		Сравнивает массив с константной строкой, оставляя массив неизменным. Его длина должна соответствовать длине константы и ограничена 255 байтами.

		>- 0
		>  массив

		<- 1, если совпал, иначе 0
		<  массив
	"""

	return (
		">>>-" + "".join((
				">[-<+>>+<]<[->+<]+>>" + increment(-string[i] - (i < len(string) - 1)) + "[[-]<<->>]"
		) for i in range(len(string))) +
		"-" + "<<[-<<+>>]>>+<<" * len(string) + "+<<<+>" + increment(-len(string)) + "[[-]<->]<"
	)

@block
def array_start_block():
	"Идёт по массиву до начала и назад"

	return "<<[<<]", ">>[>>]"

@block
def array_end_block():
	"Идёт по массиву до конца и назад"

	return ">>[>>]", "<<[<<]"

@block
def array_foreach_block():
	"Цикл по каждому элементу массива. Указатель остаётся на конце"

	return ">>[", ">>]"

# База данных

"""
	База загружается в память, как последовательность массивов по 255 байтов длиной, последний может дополняться переводами строки. После каждого массива:

	>  0, если это первый массив, иначе 1
	>  0, если это последний массив, иначе 1
	>  x1 - номер поста, который начинается в этом массиве, либо ноль. Число хранится, как 4 байта, по одной десятичной цифре в каждом, старшая спереди. Цифры хранятся в виде значений от 0 до 9
	>  x2
	>  x3
	>  x4
	>  0, если этот массив не надо отправлять в сеть, иначе 1
	>- 0
	>  0
	>  0
	>  0

	Перед базой данныз должно быть 4 нуля.

	В результате получается массив массивов, по которому тоже можно перемещаться назад-вперёд. Все функции требуют и возвращают указатель на четвёртой ячейке из этого списка.
"""

@command
def database_load_command(path):
	"Загружает базу данных из файла в память"

	path = os.path.join(root, path)

	with open(path, "rb") as file:
		data = file.read()

	result = ">>>>"

	def difference(count):
		return count if count <= 128 else -(256 - count)

	for i in range(0, len(data), 255):
		chunk = data[i: i + 255]
		chunk += b"\n" * (255 - len(chunk))

		first = i == 0
		last = i >= len(data) - 255

		result += array_set_command(chunk) + ">>[>>]>>" + (">" if first else "+>") + (">" if last else "+>") + ">>>>+>>>>>"

	return result + "<<<<"

@command
def database_go_next_command():
	"Переходит к следующему чанку"

	return ">>>>" + array_go_end_command() + ">>>>>>>>>"

@command
def database_go_back_command():
	"Переходит к предыдущему чанку"

	return "<<<<<<<<<" + array_go_start_command() + "<<<<"

@command
def database_go_end_command():
	"Переходит к последнему чанку"

	return "<<<<<<[>>>>>>" + database_go_next_command() + "<<<<<<]>>>>>>"

@command
def database_go_start_command():
	"Переходит к первому чанку"

	return "<<<<<<<[>>>>>>>" + database_go_back_command() + "<<<<<<<]>>>>>>>"

@block
def database_foreach_block():
	"Цикл по каждому чанку. Указатель остаётся на последнем"

	return "+[-", "<<<<<<[>>>>>>" + database_go_next_command() + "+<<<<<<[->>>>>>>+<<<<<<<]]>>>>>>>[-<<<<<<<+>>>>>>>]<]"

# Препроцессор

import json.decoder

JSON_decoder = json.decoder.JSONDecoder()

def parse_command(command):
	name, tail = (command.split(maxsplit = 1) + [""])[: 2]
	arguments = []
	shift = 0

	tail = tail.lstrip()

	while tail != "":
		if tail.startswith("<>"):
			shift = int(tail[2: ])
			tail = ""
		else:
			argument, length = JSON_decoder.raw_decode(tail)
			tail = tail[length: ].lstrip()

			arguments.append(argument)

	return name, arguments, shift

root = None
stack = None

def preprocess_part(code):
	result = ""

	for line in code.split("\n"):
		line = line.split("//")[0].strip()

		if line.startswith("#"):
			command = line[1: ]

			if command == "END":
				code, shift = stack.pop()
				result += code
			else:
				name, arguments, shift = parse_command(command)

				result += move(shift)

				if name in blocks:
					start, end = blocks[name](*arguments)

					stack.append((end, shift))
					shift = 0

					result += start
				elif name in commands:
					result += commands[name](*arguments)
				else:
					raise Exception("Неизвестная команда")

			result += move(-shift)
		else:
			result += line

	return result

def preprocess(code):
	global root, stack

	root = "."
	stack = []

	result = preprocess_part(code)

	if len(stack) != 0:
		raise Exception("Не хватает `END`")

	return result

def format(code):
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
		elif i in "[],.~?":
			result += reorder(fragment) + i
			fragment = ""

	result = "\n".join(result[i: i + 80] for i in range(0, len(result), 80))

	return "#!interpreter\n" + result + "\n"

import sys

sys.stdout.write(format(preprocess(sys.stdin.read())))
