import socket

server_socket = socket.socket()
server_socket.bind(('localhost', 12346))
server_socket.listen(5)

#while True:
client_socket, addr = server_socket.accept()
with open('TESTE.TXT', 'rb') as f:
    client_socket.sendfile(f, 0)
client_socket.close()