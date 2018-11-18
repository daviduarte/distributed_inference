import time
from osbrain import run_agent
from osbrain import run_nameserver


def log_message(agent, message):
    agent.log_info('Received: %s' % message)
    agent.log_info('agent: ' + str(agent))


if __name__ == '__main__':

    print("Bob")
    ns = ob.NSProxy(nsaddr='127.0.0.1:15793')
    print(ns)

    alice = ns.addr("Alice123")