import socket

CHUNK_SIZE = 8 * 1024

sock = socket.socket()
sock.connect(('localhost', 12346))
chunk = sock.recv(CHUNK_SIZE)

file  = open("kkk.txt", "wb")

while chunk:
	#print(chunk)
	file.write(chunk)
	chunk = sock.recv(CHUNK_SIZE)

sock.close()