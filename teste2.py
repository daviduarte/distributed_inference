"""
    testar como fazer o agent.each() funcionar com em um estilo OOP
"""

import time

import socket

import os

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


def reply_late(agent, message):
    print("I am the fly that landed in your soup")


if __name__ == '__main__':

    ns = run_nameserver("192.168.1.102:4444")

    agentServer = run_agent('AgentServer')
    #agentServer.bind('ASYNC_REP', handler=reply_late, alias="main")
    agentServer.bind('ASYNC_REP', handler=reply_late, alias="main")
    agentServer.bind('REP', handler=reply_late, alias="main_syn")
    
