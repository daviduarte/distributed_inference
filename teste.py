import time
from osbrain import run_agent
from osbrain import run_nameserver
from osbrain import Agent
from osbrain import Proxy
from osbrain.common import LogLevel


def process_reply():
	print("I'm the fly that came to abuse you.")

if __name__ == '__main__':

	# Setup
	#NSRemoto = Proxy('AgentServer', nsaddr="192.168.1.102:4444") #NSProxy('127.0.0.1:15793')
	alias = "some_cool_alias"

	alice = run_agent(alias, nsaddr="192.168.1.102:4444")
	#alice.set_attr(alias=alias)
	#time.sleep(1)
	#alice.connect(NSRemoto.addr('main'), alias='alice', handler=process_reply)
	#alice.connect(NSRemoto.addr('main_syn'), alias='alice_syn', handler=process_reply)
	#LogLevel("ERROR")

	alice.log_info('Cliente configurado')
	#time.sleep(1)
