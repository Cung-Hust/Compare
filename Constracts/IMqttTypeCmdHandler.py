from abc import ABCMeta, abstractmethod
from Constracts import ITransport
import logging
from GlobalVariables.GlobalVariables import GlobalVariables
from ctypes import *
import Constants.Constant as Const
import json
import threading
import time


class IMqttTypeCmdHandler(metaclass=ABCMeta):
    lib = cdll.LoadLibrary("/root/libHC_Riim_Cpp.so")
    logger: logging.Logger
    mqtt: ITransport
    globalVariable = GlobalVariables()

    def __init__(self, log: logging.Logger, mqtt: ITransport):
        self.logger = log
        self.mqtt = mqtt

    @abstractmethod
    def handler(self, data):
        pass

    def addConfigQueue(self, data):
        self.lib.C_bufferPush(Const.CONFIG_BUFFER, json.dumps(data))

    def addControlQueue(self, data):
        self.lib.C_bufferPush(Const.CONTROL_BUFFER, json.dumps(data))
        
    def send_ending_cmd(self, callback: callable):
        ending_cmd = {
            "TYPCMD": "End"
        }
        callback(ending_cmd)
        
        
    def waiting_for_handler_cmd(self):
        print("waiting for handler cmd")
        with threading.Lock():
            self.globalVariable.on_uart_cmd_processing = True       
        while self.globalVariable.on_uart_cmd_processing:
            time.sleep(1)


