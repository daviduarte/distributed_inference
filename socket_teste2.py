import socket


server_socket = socket.socket()
server_socket.bind(('', 4444))
server_socket.listen(5)

#print("emitindo um YEILSSSSDDDD")
#yield('get_model-connection_already')

client_socket, addr = server_socket.accept()

nome_modelo = "transmit.txt"

with open(nome_modelo, 'rb') as f:
	client_socket.sendfile(f, 0)

client_socket.close()
