from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class DelDevHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices = data.get("Device", [])

        db.Services.DeviceService.RemoveDeviceByCondition(
            db.Table.DeviceTable.c.DeviceAddress.in_(devices)
        )
        db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
            db.Table.GroupDeviceMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.DevicePropertyService.RemoveDevicePropertyMappingByCondition(
            db.Table.DevicePropertyMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices)
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.DeviceAddress.in_(devices)
        )
        # self.__cmd_res(devices)

    def __cmd_res(self, devices: list):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DelDevRsp",
            "Devices": []
        }
        for d in devices:
            res["Devices"].append({
                "Device": d,
                "Success": True
            })
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

