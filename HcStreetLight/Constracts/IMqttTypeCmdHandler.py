from abc import ABCMeta, abstractmethod
from Constracts import ITransport
import logging
from GlobalVariables.GlobalVariables import GlobalVariables


class IMqttTypeCmdHandler(metaclass=ABCMeta):

    logger: logging.Logger
    mqtt: ITransport
    globalVariable = GlobalVariables()

    def __init__(self, log: logging.Logger, mqtt: ITransport):
        self.logger = log
        self.mqtt = mqtt

    @abstractmethod
    def handler(self, data):
        pass
