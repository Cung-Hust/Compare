import json
import logging
import threading

import Constants.Constant as Const
from Constracts.IHandler import IHandler
from Constracts.ITransport import ITransport
from Handler.MqttTypCmdHandlers.TypeCmdHandlerManager import TypeCmdHandlerManager


class MqttDataHandler(IHandler):
    __logger: logging.Logger
    __mqtt: ITransport
    __mqttTypeCmdHandlerManager: TypeCmdHandlerManager

    def __init__(self, log: logging.Logger, mqtt: ITransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__mqttTypeCmdHandlerManager = TypeCmdHandlerManager(log, mqtt)

    def handler(self, item):
        topic = item['topic']
        message = item['msg']
        switcher = {
            Const.MQTT_CLOUD_TO_DEVICE_REQUEST_TOPIC: self.__handler_cloud_to_device_request_topic,
            Const.MQTT_DEVICE_TO_CLOUD_RESPONSE_TOPIC: self.__handler_device_to_cloud_response_topic,
        }
        func = switcher.get(topic)
        func(message)
        return

    def __handler_cloud_to_device_request_topic(self, data):
        try:
            json_data = json.loads(data)
            cmd = json_data.get("TYPCMD")
            switcher = {
                "ConfigGWRF": self.__mqttTypeCmdHandlerManager.ConfigGWRF.handler,
                "DelDev": self.__mqttTypeCmdHandlerManager.DelDev.handler,
                "GetGatewayInfor": self.__mqttTypeCmdHandlerManager.GetGatewayInfor.handler,
                "PingDevice": self.__mqttTypeCmdHandlerManager.PingDevice.handler,
                "PingGateway": self.__mqttTypeCmdHandlerManager.PingGateway.handler,
                "RequestInfor": self.__mqttTypeCmdHandlerManager.RequestInfor.handler,
                "CreateGroup": self.__mqttTypeCmdHandlerManager.CreateGroup.handler,
                "DelDevFrGroup": self.__mqttTypeCmdHandlerManager.DelDevFrGroup.handler,
                "DelGroup": self.__mqttTypeCmdHandlerManager.DelGroup.handler,
                "RebootGateway": self.__mqttTypeCmdHandlerManager.RebootGateway.handler,
                "RebootDevice": self.__mqttTypeCmdHandlerManager.RebootDevice.handler,
                "GatewayCommander": self.__mqttTypeCmdHandlerManager.GatewayCommander.handler,
                "DeviceCommander": self.__mqttTypeCmdHandlerManager.DeviceCommander.handler,
                "ConfigDev": self.__mqttTypeCmdHandlerManager.ConfigDev.handler,
                "SetDevScene": self.__mqttTypeCmdHandlerManager.SetScene.handler,
                "DelDevScene": self.__mqttTypeCmdHandlerManager.DelScene.handler,
                "DelDeviceInScene": self.__mqttTypeCmdHandlerManager.DelDeviceInScene.handler,
                "ControlRelay": self.__mqttTypeCmdHandlerManager.ControlRelay.handler,
                "ControlDevice": self.__mqttTypeCmdHandlerManager.ControlDevice.handler,
                "ActiveDevScene": self.__mqttTypeCmdHandlerManager.ActiveScene.handler,
                "StopDevScene": self.__mqttTypeCmdHandlerManager.StopScene.handler,
                "DeviceFirmURL": self.__mqttTypeCmdHandlerManager.DeviceFirmURL.handler,
                "GatewayFirmURL": self.__mqttTypeCmdHandlerManager.GatewayFirmURL.handler,
                "AddDevice": self.__mqttTypeCmdHandlerManager.AddDevice.handler,
                "SetGWScene": self.__mqttTypeCmdHandlerManager.SetGwScene.handler,
                "DelGWScene": self.__mqttTypeCmdHandlerManager.DelGwScene.handler,
                "ActiveGWScene": self.__mqttTypeCmdHandlerManager.ActiveGwScene.handler,
                "StopGWScene": self.__mqttTypeCmdHandlerManager.StopScene.handler,
            }

            func = switcher.get(cmd)
            func(json_data)

        except:
            self.__logger.error(f"mqtt data receiver in topic {Const.MQTT_CLOUD_TO_DEVICE_REQUEST_TOPIC} invalid")
            print(f"mqtt data receiver in topic {Const.MQTT_CLOUD_TO_DEVICE_REQUEST_TOPIC} invalid")

    def __handler_device_to_cloud_response_topic(self, data):
        try:
            json_data = json.loads(data)
            rqi = json_data.get("RQI")
            with threading.Lock():
                self.globalVariable.mqtt_need_response_dict.pop(rqi)
        except:
            self.__logger.error(f"mqtt data receiver in topic {Const.MQTT_DEVICE_TO_CLOUD_RESPONSE_TOPIC} invalid")
            print(f"mqtt data receiver in topic {Const.MQTT_DEVICE_TO_CLOUD_RESPONSE_TOPIC} invalid")
