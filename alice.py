import time
from osbrain import run_nameserver
from osbrain import run_agent
from osbrain.proxy import NSProxy
from osbrain import run_nameserver
from osbrain import Agent
import tensorflow as tf

bufferFrames = []

class Model(Agent):

    # Inicializa a conexão que vai pedir o buffer de frames
    def on_init(self):
        self.bind('PUSH', alias='getFrames')
        self.bind('PUSH', alias='getModel')
        oi = "kkk"

    def getModel(self):
        # Pega um modelo que cabe na memória
        self.send('getModel', 'get_the_model')

    def getFrames(self):
        # Pega os frames
        self.send('getFrames', 'get_the_frames')
        self.set_attr(model="kkkk")




class Greeter(Agent):
    def on_init(self):
        self.bind('PUSH', alias='main')

    def hello(self, name):
        self.send('main', 'Hello, %s!' % name)

        

class Bob(Agent):
    def custom_log(self, message):
        self.log_info('Received: %s' % message)

if __name__ == '__main__':

    # System deployment
    print("Alice")

    # Conecta no name server remoto
    ns = run_nameserver()
    #print(ns)

    # Cria um agent local
    alice = run_agent('Alice', nsaddr = "127.0.0.1:15793", base=Greeter)
    model = run_agent('Model', base=Model, attributes=dict(model = None, bufferFrames = None))
    model.getFrames()

    print("Enviando mensagem")
    alice.hello('Bob')

    print("testando a variavel definida o init")
    print(model.get_attr(""))

    print(model.get_attr("model"))    
    print(model.get_attr("model"))

    # Registra esse agent no nameserver
    #alice = ns.proxy('Alice0')
    
    #print(ns.agents())
    #for alias in ns.agents():
    #    print(alias)

    # Criando um proxy para esse agente
   # alice = ns.proxy('Alice123')

    #ns = NSProxy(nsaddr='127.0.0.1:10357')
    #alice = run_agent('Alice')

    # System configuration
    #addr = alice.bind('PUSH', alias='main')
    #addr = alice.bind('PUSH', transport='tcp', addr='127.0.0.1:1234')

    
    
    