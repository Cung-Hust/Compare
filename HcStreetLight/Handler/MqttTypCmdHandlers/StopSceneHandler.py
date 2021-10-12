import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading


class StopSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices_stop_list = data.get("Device", [])
        groups_stop_list = data.get("group", [])

        db.Services.EventTriggerOutputDeviceMappingService.UpdateEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices_stop_list),
            {
                "IsEnable": False
            }
        )

        db.Services.EventTriggerOutputGroupMappingService.UpdateEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.GroupId.in_(groups_stop_list),
            {
                "IsEnable": False
            }
        )
        # self.__cmd_res(data["ID"], devices_stop_list, groups_stop_list)

    def __cmd_res(self, scene: int, devices: list, groups: list):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "StopSceneRsp",
            "ID": scene,
            "Devices": [],
            "Groups": []
        }

        for d in devices:
            res["Devices"].append({
                "Device": d,
                "Success": True
            })
        for g in groups:
            res["Groups"].append({
                "Group": g,
                "Success": True
            })
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

