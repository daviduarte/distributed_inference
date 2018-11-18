import time

import socket

import os

import osbrain
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import Agent
from osbrain.common import LogLevel

from PIL import Image, ImageDraw
import numpy as np

import signal
import sys
import time

from osbrain.proxy import Proxy

osbrain.config['TRANSPORT'] = 'tcp'

END_REMOTO = "192.168.1.4"


NUM_AJUSTA_VAZAO = 5			# Ajusta a média do tempo a cada 5 solicitações
PATH = os.path.dirname(os.path.abspath(__file__))
print(PATH)

server_socket = None
agentServer = None
models = []
ns = run_nameserver(END_REMOTO + ":4444")

# Configura o signal de saída
def signal_handler(sig, frame):
        print('Você pressionou Ctrl+C!')
        ns.shutdown()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


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

# Seleciona o modelo mais apropriado para enviar ao cliente
# @param solicitacao - um objeto da classe Solicitação com as restrições do cliente
# @return - uma string com o nome do modelo selecionado
def selecionarModelo(solicitacao):
	print("Selecionando um modelo")
	return PATH + "/models/0123456789.pb"


# Primeiro, pesquisa o cliente pelo alias na lista de clientes. Isso é uma tarefa custosa e, no futuro, deve-se ser pensado alguma
# solução arquitetural mais eficiente. Depois, pega os dados de conexão e seleciona os frames que mais se adequal am cliente
def obtemFrames(agent, solicitacao):
	#print("Caler: ")
	#print(solicitacao.aliasCaller)

	#print("model")
	#print(agent.get_attr("models")[0].clients)

	model = agent.get_attr("models")[0]
	client = model.clients[str(solicitacao.aliasCaller)]
	latenciaMax = model.latenciaMax 

	#print("media tempo:")
	#print(client.mediaTempo)

	# Primeiro pega 'client.bufferSize' frames
	now = getNow()	
	aux = []

	print(len(model.queue))
	tamBuffer = len(model.queue)

	#try:
	if tamBuffer > 0: 		# Se a lista NÃO estive vazia

		qtdFrames = client.bufferSize
		count = 0
		i = 0
		while count < qtdFrames and i < tamBuffer:
			frame = model.queue.pop(0)		# frame = [frame, timestamp]	
			if frame[1] + (model.latenciaMax) > now:		# Se o frame ainda estiver na validade, senão, tira do buffer
				aux.append(frame)
				count = count + 1
			i = i + 1

		print("Obtendo " + str(count) + "/" + str(qtdFrames) + " frames")
		print("Media tempo dos ultimos " + str(NUM_AJUSTA_VAZAO) + " frames: " + str(client.mediaTempo))

	#except:
		#print("Erro. Provavelmente por causa de race condition. Arrumar o lock depois")

	return aux

	#if client.mediaTempo == 0

# Retorna a quantidade de microsegundos que representa o agora
def getNow():
	timestamp = str(time.time())
	#timestamp = timestamp.replace(".", "")	
	return float(timestamp)

def ajustarVazao(agent, solicitacao):

	alias = str(solicitacao.aliasCaller)
	model = agent.get_attr("models")
	clients = model[0].clients

	client = None

	if alias in clients:
		client = clients[alias]
	else:
		print("ERRO GRAVE! O CLIENT NÃO FOI ENCONTRADO PARA ATUALIZAR A VAZÃO.")

	mediaTempoAux = client.mediaTempoAux
	qtdMediaTempo = client.qtdMediaTempo
	startTime = client.startTime
	mediaTempo = client.mediaTempo
	bufferSize = client.bufferSize
	latenciaMax = model[0].latenciaMax


	endTime = getNow()
	latencia = endTime - startTime

	qtdMediaTempo = qtdMediaTempo + 1
	
	mediaTempoAux = mediaTempoAux + latencia

	if qtdMediaTempo >= NUM_AJUSTA_VAZAO:
		mediaTempo = mediaTempoAux / NUM_AJUSTA_VAZAO
		qtdMediaTempo = 0
		mediaTempoAux = 0
		client.mediaTempo = mediaTempo	

		# Ajustar a vazão
		if mediaTempo < latenciaMax:
			bufferSize = bufferSize + 1
		else:			
			bufferSize = bufferSize - 1


	client.bufferSize = bufferSize
	client.qtdMediaTempo = qtdMediaTempo	
	client.qtdTempoAux = 0
	client.mediaTempoAux = mediaTempoAux


	agent.set_attr(models = model)

	#print("Média do tempo que demorou *************")
	#print(agent.get_attr("models")[0].clients[alias].qtdMediaTempo)
	#print(agent.get_attr("models")[0].clients[alias].mediaTempo)
	#print(agent.get_attr("models")[0].clients[alias].mediaTempoAux)
	#print(agent.get_attr("models")[0].clients[alias].startTime)


def reply_now(agent, message):
	print("Recebendo uma mensagem síncrona: ")
	print(message)

def reply_late(agent, message):

	if message.tipo == 'get_model':		
		#print("Enviando um modelo para o cliente")

		server_socket = socket.socket()
		server_socket.bind(('', 1112))
		server_socket.listen(5)
		
		#print("emitindo um YEILSSSSDDDD")
		#yield('get_model-connection_already')

		client_socket, addr = server_socket.accept()

		nome_modelo = selecionarModelo(message)

		with open(nome_modelo, 'rb') as f:
			client_socket.sendfile(f, 0)

		client_socket.close()

		#print("******************* chegou aki")
		return('get_model-success')

	elif message.tipo == 'get_frames':	

		#print("Enviando frames para o cliente")

		#print("tesde de como obter o alias do cliente que chamou")
		#print(agent)
		reply = Reply()
		reply.message = "reply_frame"	

		reply.frames = obtemFrames(agent, message)	# Seleciona a quantidade e quais frames enviar		

		# Configura o tempo de início que essa solicitação chegou
		clients = agent.get_attr("models")[0].clients
		alias = message.aliasCaller
		
		now = getNow()

		if alias in clients:
			clients[alias].startTime = now
		else:
			print("ERRO GRAVE: CLIENTE NÃO ENCONTRADO")

		#reply.frames = [4,5,6]

		return reply
	
	# Insere os frames recebidos DE FORMA ORDENADA pelo timestamp
	elif message.tipo == 'set_frames':			
		#print("Recebendo uma lista de buffers processados")
		framesProcessados = message.bufferResposta	

		model = agent.get_attr("models")[0]
		
		queueBack = model.queueBack

		if len(queueBack) == 0:
			print("Queue back está vazia")
			queueBack = framesProcessados
		else:
			i = 0
			for i in range(len(framesProcessados)):
				j = 0
				entrou = 0
				for j in range(len(queueBack)):
					if int(framesProcessados[i][1]) < int(queueBack[j][1]):
						#queueBack = queueBack.tolist()	# Em alguns momentos aparece um erro falando que queueBack é um array. Resolve isso aqui
						entrou = 1
						queueBack.insert(j, framesProcessados[i])
						break
				if entrou == 0:	# Se o frame for maior que todos os outros frames presentes no buffer, coloca no final
					queueBack.append(framesProcessados[i])

		#print("LISTA ORDENADA SEM SHAPE:")
		#print(np.array(queueBack).shape)

		model.queueBack = queueBack
		agent.set_attr(models = [model])
		
		# Ajusta o client.mediaTempo
		ajustarVazao(agent, message)

		reply = Reply()
		reply.message = "reply_set_frame"
		reply.error = "success"

		return reply
		
	return("erro");

def inserirImagens(agent):
	
	aux = []
	for i in range(100):
		image = Image.open("../examples/" + str(i) + ".png")
		#print(image.getdata())
		(im_width, im_height) = image.size
		image = np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
		aux.append(image)

	aux = np.array(aux)
	print("Inserindo um vetor de imagens de shape")
	print(aux.shape)

	model = agent.get_attr('models')[0]
	model.addFramesBuffer(aux)
	agent.set_attr(models = [model])



def mostrarQueue(agent):
	print("Queue de frames:")
	count = np.asarray(agent.get_attr('models')[0].queue).shape
	if count == 0:
		sys.exit()
	print(np.asarray(agent.get_attr('models')[0].queue).shape)

	#print("Queue de frames processados:")
	#print(np.array(agent.get_attr('models')[0].queueBack).shape)	



'''
def process_reply(agent, message):
    agent.log_info('Processed reply: %s' % message)
'''


# Armazena os modelos para distribuir o processamento

class Client():
	def __init__(self):
		self.alias = ""			# Um ID único
		self.mediaTempo = 0		# Media de tempo que um frame demora para ser processado
		self.mediaTempoAux = 0	# Vai somando até dividir por 'self.qtdMediaTempo'
		self.qtdMediaTempo = 0	# Variável auxiliar qpara caldular a 'self.mediaTempo'
		self.bufferSize = 5		# Quantidade de frames que é enviado para o cliente
		self.startTime = 0		# Guarda o tempo no qual um cliente solicita um conjunto de frames
		self.endTime = 0		# Guarda o tempo no qual o cliente devolve os frames processados

class Model():
	def __init__(self):
		self.id = ""			# Um ID único 
		self.model = ""			# Path do modelo
		self.queue = []			# Fila que armazena os frames para processamento
		self.rate = 0;			# Taxa de chegada de frames
		self.queueBack = []		# Fila que armazena os frames processados
		self.tamFrames = 0		# Tamanho dos frames
		self.clients = {}		# Índices do vetor connections. Cada client pode estar vinculado a somente 1 modelo
		self.latenciaMax = 500	# Quantidade de maxima de segundos que um frame deve demorar para ser processado e retornado

	def stop(self):
		print("Parando o modelo")

	def getObterQueueBack(self):
		print("Obter a fila de volta")

	# Add a list of frames in 'self.queue'
	# @param listFrames A list of frames of size 'tamFrames'
	def addFramesBuffer(self , listFrame):
		timestamp = getNow()
		newList = []
		# Pra cada item da listFrame, add o timestamp
		for i in range(len(listFrame)):
			newList.append( [listFrame[i], timestamp] )
		
		#newList = np.array(newList)
		print("Inserindo um vetor de imagens de shape")
		print(np.array(newList).shape)
		#print(newList)
		self.queue = newList

class AgentServer(Agent):

	def on_init(self):
		self.log_info("Servidor iniciado")

		# Inicialmente estamos trabalhando apenas com 1 model
		models = [Model()]
		self.set_attr(connections = {}, models=models)


	# Add um novo modelo em 
	def addModel(self):
		self.models.append("1")

	def removeModel(self, id):
		print("remode model")






agentServer = run_agent('AgentServer', base=AgentServer)
#agentServer.bind('ASYNC_REP', handler=reply_late, alias="main")
agentServer.bind('ASYNC_REP', handler=reply_late, alias="main")
agentServer.bind('REP', handler=reply_now, alias="main_syn")

#agentServer.connect(addr, alias='alice', handler=process_reply)
LogLevel("ERROR")

# insere alguns frames no buffer
inserirImagens(agentServer)
#agentServer.each(1, inserirImagens)
agentServer.each(1, mostrarQueue)


while 1:
	for alias in ns.agents():
		if alias != "AgentServer":
			#print(alias)
			
			if alias not in agentServer.get_attr('connections'):

				print("Novo cliente conectado *******")
				# Primeiro, coloca o novo agente na lista de conexões 
				proxy = Proxy(alias)

				oi = agentServer.get_attr('connections')
				oi[alias] = proxy
				agentServer.set_attr(connections = oi)


				#print(proxy)
				

				# Como só temos 1 modelo, podemos bindar o cliente na mesma hora da conexão. Depois isso terá que ser alterado
				objeto = agentServer.get_attr("models")
				objeto[0].clients[str(alias)] = Client()
				agentServer.set_attr(models=objeto)

				#print("model")
				#print(agentServer.get_attr("models")[0].clients)


				#agentServer.connect(proxy.addr('main'), alias=alias, handler=process_reply)
				#agentServer.send(alias, 'Hello, Alice!')
				#agentServer.log_info('I am done!')
				#agentServer.log_info('Waiting for Alice to reply...')


	time.sleep(1)



ns.shutdown()