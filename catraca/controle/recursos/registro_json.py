#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import datetime
from catraca.logs import Logs
from catraca.util import Util
from catraca.modelo.dados.servidor_restful import ServidorRestful
from catraca.modelo.dao.registro_dao import RegistroDAO
from catraca.modelo.entidades.registro import Registro
from catraca.modelo.dao.catraca_dao import CatracaDAO
from catraca.modelo.dao.turno_dao import TurnoDAO


__author__ = "Erivando Sena" 
__copyright__ = "(C) Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br" 
__status__ = "Prototype" # Prototype | Development | Production 


class RegistroJson(ServidorRestful):
    
    log = Logs()
    registro_dao = RegistroDAO()
    
    hora_atual = datetime.datetime.strptime('00:00:00','%H:%M:%S').time()
    hora_inicio = datetime.datetime.strptime('00:00:00','%H:%M:%S').time()
    hora_fim = datetime.datetime.strptime('00:00:00','%H:%M:%S').time()
    
    def __init__(self, ):
        super(RegistroJson, self).__init__()
        ServidorRestful.__init__(self)
        self.obtem_turno()
        
    def registro_get(self):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(servidor) + "registro/jregistro/" + str(self.hora_inicio) + "/" +str(self.hora_fim)
                header = {'Content-type': 'application/json'}
                r = requests.get(url, auth=(self.usuario, self.senha), headers=header)
                print "status HTTP: " + str(r.status_code)
                dados  = json.loads(r.text)
    
                if dados["registros"] is not []:
                    for item in dados["registros"]:
                        obj = self.dict_obj(item)
            
                        if obj.id:
                            lista = self.registro_dao.busca(obj.id)
                            if lista is None:
                                print "nao existe - insert " + str(obj.data)
                                self.registro_dao.insere(obj)
                                print self.registro_dao.aviso
    #                         else:
    #                             print "existe - update " + str(obj.data)
    #                             self.registro_dao.atualiza_exclui(obj, False)
    #                             print self.registro_dao.aviso
        except Exception as excecao:
            print excecao
            self.log.logger.error('Erro obtendo json registro.', exc_info=True)
        finally:
            pass
        
    def dict_obj(self, formato_json):
        registro = Registro()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            
            if item == "regi_id":
                registro.id = self.dict_obj(formato_json[item])
            if item == "regi_data":
                registro.data = self.dict_obj(formato_json[item])
            if item == "regi_valor_pago":
                registro.pago = self.dict_obj(formato_json[item])
            if item == "regi_valor_custo":
                registro.custo = self.dict_obj(formato_json[item])
            if item == "cart_id":
                registro.cartao = self.dict_obj(formato_json[item])
            if item == "turn_id":
                registro.turno = self.dict_obj(formato_json[item])
            if item == "catr_id":
                registro.catraca = self.dict_obj(formato_json[item])
                
        return registro
    
    def lista_json(self, lista):
        if lista:
            for item in lista:
                registro = {
                    "regi_data":str(item[1]),
                    "regi_valor_pago":float(item[2]),
                    "regi_valor_custo":float(item[3]),
                    "cart_id":item[4],
                    "turn_id":item[5],
                    "catr_id":item[6]
                }
                self.registro_post(registro)
                #self.registro_dao.mantem(self.registro_dao.busca(item[0]),True)

    def objeto_json(self, obj):
        if obj:
            registro = {
                "regi_data":str(obj.data),
                "regi_valor_pago":float(obj.pago),
                "regi_valor_custo":float(obj.custo),
                "cart_id":obj.cartao.id,
                "turn_id":obj.turno.id,
                "catr_id":obj.catraca.id
            }
            self.registro_post(registro)
            
    def registro_post(self, formato_json):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(servidor) + "registro/insere"
                print url
                header = {'Content-type': 'application/json'}
                r = requests.post(url, auth=(self.usuario, self.senha), headers=header, data=json.dumps(formato_json))
                #print r.headers['content-type']
                #print r.headers
                print r.text
                print r.status_code
                #print 'requests.post: '+ str(formato_json)
        except Exception as excecao:
            print excecao
            self.log.logger.error('Erro enviando json registro.', exc_info=True)
        finally:
            pass
        
    def obtem_turno(self):   
        catraca = CatracaDAO().busca_por_ip(Util().obtem_ip())
        turnos = TurnoDAO().busca_por_catraca(catraca)
        if turnos:
            turnos.sort()
            for turno in turnos:
                self.hora_atual = Util().obtem_hora()
                self.hora_inicio = datetime.datetime.strptime(str(turno[1]),'%H:%M:%S').time()
                self.hora_fim = datetime.datetime.strptime(str(turno[2]),'%H:%M:%S').time()
                if ((self.hora_atual >= self.hora_inicio) and (self.hora_atual <= self.hora_fim)):
                    return turno
                    break
            return None
        