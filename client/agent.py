import time

import socket
import numpy as np

import os
import psutil
import random
import sys

import osbrain
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import Agent
from osbrain.proxy import NSProxy
from osbrain.proxy import Proxy
from osbrain.common import LogLevel

from PIL import Image, ImageDraw

import tensorflow as tf

# Configura o PYTHONPATH
try:
    sys.path.index('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research') # Or os.getcwd() for this directory
    sys.path.index('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research/slim')
    sys.path.index('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research/object_detection')
except ValueError:
    sys.path.append('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research') # Or os.getcwd() for this directory
    sys.path.append('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research/slim')
    sys.path.append('/home/davi/Documentos/Mestrado/Projeto_IA_SD/models/research/object_detection')

END_REMOTO = "192.168.1.4"

PATH = os.path.dirname(os.path.abspath(__file__))
PATH_MODEL = PATH + "/frozen_graph_model.pb"
PATH_LABELS = PATH + "/labels.pbtxt"
print(PATH)
PORCENTAGEM_MEM_DISPONIVEL = 0.1	# Quanto da memória disponível usar

graph_global = None

osbrain.config['TRANSPORT'] = 'tcp'


# Gambiarra para armazenar o graph (que é muito grande) no agente
def loadModel():
	global graph_global
	# We load the protobuf file from the disk and parse it to retrieve the 
	# unserialized graph_def
	with tf.gfile.GFile(PATH_MODEL, "rb") as f:
		graph_def = tf.GraphDef()
		graph_def.ParseFromString(f.read())

	# Then, we import the graph_def into a new Graph and returns it 
	with tf.Graph().as_default() as graph:
		# The name var will prefix every op/nodes in your graph
		# Since we load everything in a new graph, this is not needed
		tf.import_graph_def(graph_def, name="prefix")

	graph_global = graph
	#time.sleep(10)


class Solicitacao():
	def __init__(self):
		#print("Iniciando a classe de solicitação de modelo")
		self.tipo = None
		self.aliasCaller = None

		# Variáveis utilizadas para solicitar um modelo
		self.tamMaxModel = None

		# Variáveis utilizadas para solicitar frames
		self.tamMem = float("Inf")

		# Variáveis utilizadas para enviar o bufferResposta
		self.bufferResposta = None

class Reply():
	def __init__(self):
		self.message = None
		self.error = None

		# Variáveis utilizadas para enviar uma lista de frames
		self.frames = []		

# Cada cliente precisa ter um alias único. Portanto, gera um novo alias utilizando o endereço de IP
def gerarAlias():

	string = ""
	for x in range(10):
		string = string + str(random.randint(1,101))

	return string


def process_now(agent, message):
	print("oi")

# As mensagens são do tipo: flag-status. Por ex: get_model-success
def process_reply(agent, message):
	#tipo = message.split('-')

	if message.message == "reply_frame":
		#print("*************** Lista de frames: ")
		#print(message.frames)
		agent.set_attr(buffer=message.frames)
	elif message.message == "reply_set_frame":
		if message.error == "success":
			nao_faz = "nada"

		

	#agent.log_info('tipo: ' + str(tipo))

def init_global(agent):
	agent.processFrames()	

def processFrames(agent):
	agent.processFrames()


# Classe do agent
class Client(Agent):
	def on_init(self):
		self.log_info("Ciente iniciado")
		self.set_attr(alias=None, buffer=[], bufferResposta=[], memTotal=None, porCentoMem=None, tamFrame=None, graph=None)



		#return graph

	def sendMessage(self, command):		

		if command == "get_model":
			solicitacao = Solicitacao()
			solicitacao.aliasCaller = self.get_attr('alias')
			solicitacao.tipo = "get_model"
			solicitacao.tamMaxModel = psutil.virtual_memory()[1] * PORCENTAGEM_MEM_DISPONIVEL	# Memória utilizável em bytes
			self.send("alice", solicitacao)

			# A solicitação para abrir um socket demora um pouco pra chegar. Por isso, aguarda aguns segundos. Caso ainda não dê tempo,
			#, trata a exceção e tenta novamente

			time.sleep(1)
			
			CHUNK_SIZE = 8 * 1024

			sock = socket.socket()
			sock.connect(('localhost', 1112))
			chunk = sock.recv(CHUNK_SIZE)

			file  = open(PATH + "/frozen_graph_model.pb", "wb")

			while chunk:
				#print(chunk)
				file.write(chunk)
				chunk = sock.recv(CHUNK_SIZE)

			sock.close()					
			#print("chegou akiiii ;)")

		elif command == "get_frames":

			solicitacao = Solicitacao()
			solicitacao.tipo = "get_frames"
			solicitacao.tamMem = float("Inf")	# Calcular depois a quantidade de memória que pode ser utilizada
			solicitacao.aliasCaller = self.get_attr('alias')

			self.send("alice", solicitacao)

		# Envia os frames já processados para o servidor
		elif command == "set_frames":
			solicitacao = Solicitacao()
			solicitacao.tipo = "set_frames"			
			solicitacao.bufferResposta = self.get_attr('bufferResposta')
			solicitacao.aliasCaller = self.get_attr('alias')

			self.send("alice", solicitacao)



		# Método principal que recebe o modelo e processa os frames
	def init_kkk(self):
		#self.sendMessage('get_frames')
		loadModel()

#		init_global(self)
		#while 1:
		#	self.processFrames()

	def processFrames(self):		
		self.sendMessage("get_frames")			# Atualiza o parâmetro 'buffer'
		time.sleep(1)
		buffer_local = self.get_attr('buffer')	# Obtém o parâmetro 'buffer'

		#print("buffer local:")
		#print(np.array(buffer_local).shape)
		imgs = []
		timestamps = []		# Armazena os timestamps de cada frame para ficar fácil colocar de volta nas imagens processadas
		for i in range(len(buffer_local)):
			imgs.append(buffer_local[i][0])
			timestamps.append(buffer_local[i][1])

		imgs = np.array(imgs)
		timestamps = np.array(timestamps)
		#print("entrou no looping")


		if not buffer_local:
			print("Não há frames para processar")
		else:
			#print("imgs:")
			#print(imgs.shape)
			self.inferencia(imgs, timestamps)			

		#time.sleep(2)

	def inferencia(self, tensor, timestamps):
		# Carrega alguma imagem para teste
		#image = Image.open(PATH + "/imgs/2.jpg")
		#print(image.getdata())
		#(im_width, im_height) = image.size
		#image = np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


		#im = Image.open('imgs/2.jpg')
		#im = im.resize((300, 300), Image.ANTIALIAS)
		#draw = ImageDraw.Draw(im)


		#image = np.zeros((300,300,3))
		x = graph_global.get_tensor_by_name('prefix/image_tensor:0')
		y = graph_global.get_tensor_by_name('prefix/detection_boxes:0')

		with tf.Session(graph=graph_global) as sess:
			#print("ok, criou a sessão")
			#self.set_attr(bufferResposta = sess.run(y, feed_dict={x: np.expand_dims(image, 0)}))
			res = sess.run(y, feed_dict={x: tensor})
			

			#print("DIMENSÕES DO VETOR PROCESSADO: ")
			#print(res.shape)

		# Coloca o timestamp original no frame: [frame, timestamp]
		aux = []
		res = res.tolist()

		for i in range(len(res)):
			aux.append([res[i], timestamps[i]])
		#aux = aux[0]
		#aux = np.array(aux)

		#print("Classe do resultado da inferência: ")
		#print(type(aux))
		#print("Print resultado da inferência: ")
		#print(aux)
		#print("Tamanho do resultado da inferência: ")
		#print(len(aux))		
		#print("Shape: ")

		#print(.shape)
		
		self.set_attr(bufferResposta = aux)
		self.sendMessage("set_frames")
		#time.sleep(0.1)




if __name__ == '__main__':

	# Setup
	NSRemoto = Proxy('AgentServer', nsaddr=END_REMOTO + ":4444") #NSProxy('127.0.0.1:15793')
	alias = gerarAlias()
	alice = run_agent(alias, nsaddr=END_REMOTO + ":4444", base=Client)
	alice.set_attr(alias=alias)
	time.sleep(1)
	alice.connect(NSRemoto.addr('main'), alias='alice', handler=process_reply)
	alice.connect(NSRemoto.addr('main_syn'), alias='alice_syn', handler=process_now)

	LogLevel("ERROR")


	alice.log_info('Cliente configurado')
	time.sleep(1)
	alice.send("alice_syn", "Enviando dado pelo canal sincrono")
	reply = alice.recv("alice_syn")
	print(reply)


	# Produção 
	#alice.sendMessage("get_model")

	#

	#print("chegou aki 1")
	#print(graph_global)

	time.sleep(5)
	alice.init_kkk()	
	alice.each(0, init_global)
	#alice.each(1, init_global) 

	# We launch a Session
	#x = graph.get_tensor_by_name('prefix/Placeholder/inputs_placeholder:0')
	#y = graph.get_tensor_by_name('detection_boxes:0')
	#with tf.Session(graph=graph) as sess:
	#y_out = sess.run()

	time.sleep(2)

	#ns.shutdown()