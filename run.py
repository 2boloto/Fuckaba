#!/usr/bin/python3

server = "./fuckaba.bf"
address = "127.0.0.1", 8008

import subprocess
import socket

with socket.socket() as s:
	s.bind(address)
	s.listen()

	process = subprocess.Popen([server], stdin = subprocess.PIPE, stdout = subprocess.PIPE)

	connection = None

	while True:
		command = process.stdout.read(1)[0]
		result = b""

		if command == 0:
			print("Ожидание соединения")

			connection = s.accept()[0]

			print("Соединение начато")
		elif command == 1:
			print("Получение данных")

			received = connection.recv(255)

			print("Данные получены {!r} (длина: {})".format(received, len(received)))

			result = bytes([len(received)]) + received
		elif command == 2:
			data = process.stdout.read(process.stdout.read(1)[0])

			print("Отправка данных {!r} (длина: {})".format(data, len(data)))

			result = bytes([connection.send(data)])

			print("Отправленно байтов: {}".format(result[0]))
		elif command == 3:
			print("Закрытие соединения")

			connection.close()

			print("Соединение закрыто")
		else:
			print("Неизвестная команда {}".format(command))

		process.stdin.write(result)
		process.stdin.flush()
