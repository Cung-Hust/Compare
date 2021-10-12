from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import json
from Database.Db import Db
import uuid
import Constants.Constant as Const
import threading


class ControlRelayHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))
        relays_control = data.get("Control")
        db.Services.GatewayService.UpdateGatewayById(Const.GATEWAY_ID, relays_control)

        self.__cmd_res()

    def __cmd_res(self):
        db = Db()
        with threading.Lock():
            rel2 = db.Services.GatewayService.FindGatewayById(Const.GATEWAY_ID)

        gateway_info = dict(rel2.first())
        gateway_info_res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "GWRelayStt",
            "Relay_1": gateway_info.get("Relay_1"),
            "Relay_2": gateway_info.get("Relay_2"),
            "Relay_3": gateway_info.get("Relay_3"),
            "Relay_4": gateway_info.get("Relay_4"),
            "Scene_1": gateway_info.get("Scene_1"),
            "Scene_2": gateway_info.get("Scene_2"),
            "Scene_3": gateway_info.get("Scene_3"),
            "Scene_4": gateway_info.get("Scene_4"),
            "Minute_1": gateway_info.get("Minute_1"),
            "Minute_2": gateway_info.get("Minute_2"),
            "Minute_3": gateway_info.get("Minute_3"),
            "Minute_4": gateway_info.get("Minute_4"),
        }
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[gateway_info_res["RQI"]] = gateway_info_res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(gateway_info_res))

