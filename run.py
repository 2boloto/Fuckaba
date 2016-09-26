#!/usr/bin/python3

import sys
import subprocess
import socket

with socket.socket() as s:
	s.bind((sys.argv[2], int(sys.argv[3])))
	s.listen()

	process = subprocess.Popen([sys.argv[1]], stdin = subprocess.PIPE, stdout = subprocess.PIPE)

	while True:
		command = process.stdout.read(1)[0]
		result = b""

		if command == 0:
			try:
				connection = s.accept()[0]

				result += b"\x00"
			except ConnectionAbortedError:
				result += b"\x01"
		elif command == 1:
			length = process.stdout.read(1)[0]

			try:
				received = connection.recv(length)

				result += b"\x00" + bytes([len(received)]) + received
			except ConnectionResetError:
				result += b"\x01"
		elif command == 2:
			length = process.stdout.read(1)[0]
			data = process.stdout.read(length)

			try:
				result += b"\x00" + bytes([connection.send(data)])
			except (ConnectionResetError, BrokenPipeError):
				result += b"\x01"
		elif command == 3:
			connection.close()

		process.stdin.write(result)
		process.stdin.flush()
