import socket
import os

CHUNK_SIZE = 8 * 1024
PATH = os.path.dirname(os.path.abspath(__file__))

sock = socket.socket()
sock.connect(('localhost', 4444))
chunk = sock.recv(CHUNK_SIZE)

file  = open(PATH + "/kkk_received.txt", "wb")

while chunk:
	print(chunk)
	file.write(chunk)
	chunk = sock.recv(CHUNK_SIZE)

sock.close()					