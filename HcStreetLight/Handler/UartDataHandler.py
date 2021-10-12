import json
import logging
import Constants.Constant as Const
from Constracts.IHandler import IHandler
from Constracts.ITransport import ITransport


class UartDataHandler(IHandler):
    __logger: logging.Logger
    __uart: ITransport

    def __init__(self,  log: logging.Logger, uart: ITransport):
        self.__logger = log
        self.__uart = uart

    def handler(self, item):
        opcode = item[2] << 8 | item[3]
        switcher = {

        }
