from pade.misc.utility import display_message
from pade.misc.common import set_ams, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=False)
        display_message(self.aid.localname, 'Hello World!')

if __name__ == '__main__':

    set_ams('localhost', 8000, debug=False)

    agents = list()

    agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
    agente_hello.ams = {'name': 'localhost', 'port': 8000}
    agents.append(agente_hello)

    start_loop(agents, gui=True)