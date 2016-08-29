#!/usr/bin/python3

server = "./fuckaba.bf"
address = "127.0.0.1", 8008

import subprocess
import socket

with socket.socket() as s:
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	s.bind(address)
	s.listen()

	process = subprocess.Popen([server], stdin = subprocess.PIPE, stdout = subprocess.PIPE)

	connection = None

	while True:
		command = process.stdout.read(1)[0]
		result = b""

		if command == 0:
			print("Ожидание соединения")

			try:
				connection = s.accept()[0]

				print("Соединение начато")

				result += b"\x00"
			except ConnectionAbortedError:
				print("Соединение отменено")

				result += b"\x01"
		elif command == 1:
			length = process.stdout.read(1)[0]

			print("Получение данных (длина: {})".format(length))

			try:
				received = connection.recv(length)

				print("Данные получены {!r} (длина: {})".format(received, len(received)))

				result += b"\x00" + bytes([len(received)]) + received
			except ConnectionResetError:
				print("Соединение прервано")

				result += b"\x01"
		elif command == 2:
			length = process.stdout.read(1)[0]
			data = process.stdout.read(length)

			print("Отправка данных {!r} (длина: {})".format(data, len(data)))

			try:
				sent = connection.send(data)

				print("Отправленно байтов: {}".format(sent))

				result += b"\x00" + bytes([sent])
			except ConnectionResetError:
				print("Соединение прервано")

				result += b"\x01"
		elif command == 3:
			print("Закрытие соединения")

			connection.close()

			print("Соединение закрыто")
		else:
			print("Неизвестная команда {}".format(command))

		process.stdin.write(result)
		process.stdin.flush()
