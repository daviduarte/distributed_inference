import time

from osbrain import run_agent
from osbrain import run_nameserver
from osbrain.proxy import Proxy

# Armazena as conexões atuais
connections = {}


def process_reply(agent, message):
    agent.log_info('Processed reply: %s' % message)


ns = run_nameserver("127.0.0.1:15793")

agentServer = run_agent('AgentServer')
#agentServer.connect(addr, alias='alice', handler=process_reply)


while 1:
	for alias in ns.agents():
		if alias != "AgentServer":
			print(alias)
			
			if alias not in connections:

				# Primeiro, coloca o novo agente na lista de conexões 
				proxy = Proxy(alias)
				connections[alias] = proxy

				print(Proxy(alias))
				agentServer.connect(proxy.addr('main'), alias='alice', handler=process_reply)
				agentServer.send('alice', 'Hello, Alice!')
				agentServer.log_info('I am done!')
				agentServer.log_info('Waiting for Alice to reply...')


	time.sleep(1)



ns.shutdown()