import time
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import Agent
from osbrain.proxy import Proxy

#from osbrain.logging import Logger

# A dictionary that storages a agent alias and Proxy
# alias => proxy
connections = {}

class AgentServer(Agent):
	
	def on_init(self):
		self.oi = "kkk"
		self.bind('PUSH', alias='main')

	def custom_log(self, message):
		# Lógica para atribuir uma imagem ao agent
		self.log_info('Received: %s' % message)		

if __name__ == '__main__':

	# System deployment
	ns = run_nameserver("127.0.0.1:15793")

	# Cria um agent que vai ficar encarregado de fazer os corres do servidor
	agentServer = run_agent('agentServer', nsaddr = "127.0.0.1:15793", base=AgentServer)

	while 1:
		for alias in ns.agents():
			if alias != "agentServer":
				print(alias)

				if alias not in connections:
					proxy = Proxy(alias)
					connections[alias] = proxy				
					agentServer.connect(proxy.addr('main'), handler='custom_log')

		time.sleep(5)
