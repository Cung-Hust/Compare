from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid


class PingDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        res = {
            "RQI": data.get("RQI"),
            "TYPCMD": "PingDeviceRsp",
            "Device": data.get("Device"),
            "Success": True
        }
        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(res))

        cmd_send_to_device = {
            "TYPCMD": "PingDeviceRsp",
            "Device": data.get("Device")
        }

        self.addControlQueue(cmd_send_to_device)
        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()