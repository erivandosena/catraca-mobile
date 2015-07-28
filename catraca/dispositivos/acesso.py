#!/usr/bin/env python
# -*- coding: latin-1 -*-

import time
import threading
from threading import Thread
from catraca.logs import Logs
from catraca.dispositivos.leitorcartao import LeitorCartao
from catraca.dispositivos.threadcatraca import ThreadCatraca

__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br" 
__status__ = "Prototype" # Prototype | Development | Production 


class Acesso(ThreadCatraca):
    
    log = Logs()
    #threadLock = threading.Lock()
    
    def __init__(self, threadID, name, counter):
        #super(Acesso, self).__init__()
        Thread.__init__(self)
        #self.threadID = threadID
        #self.name = name
        #self.counter = counter

    def run(self):
        print "%s Rodando... " % self.name
        #self.threadLock.acquire()
        #self.print_time(self.name, self.counter, 2)
        # Free lock to release next thread
        #self.threadLock.release()
        self.ler_cartao()
        
#     def print_time(self,threadName,delay,counter):
#         while counter:
#         #while True:    
#             time.sleep(delay)
#             print "%s: %s" % (threadName, time.ctime(time.time()))
#             counter -= 1
        
    def ler_cartao(self):
        try:
            LeitorCartao().ler()
        except SystemExit, KeyboardInterrupt:
            raise
        except Exception:
            self.log.logger.error('Erro iniciando leitura do cartao.', exc_info=True)
        finally:
            pass
    
    def nome(self):
        return 'Leitor RFID.'
            