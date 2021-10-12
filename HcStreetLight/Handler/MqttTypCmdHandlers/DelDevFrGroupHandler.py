import threading
import uuid

from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import json
import Constants.Constant as Const
from Database.Db import Db
from sqlalchemy import and_


class DelDevFrGroupHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        mqttReceiveCommandResponse = {
            "RQI": data["RQI"]
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        db = Db()

        devices = data.get("Device", [])
        groupId = data.get("GroupID", [])

        db.Services.GroupDeviceMappingService.RemoveGroupDeviceMappingByCondition(
            and_(db.Table.GroupDeviceMappingTable.c.GroupId == groupId,
                 db.Table.GroupDeviceMappingTable.c.DeviceAddress.in_(devices)
                 )
        )
        r = {
            "devices_success": devices,
            "devices_failure": []
        }
        # self.__cmd_res(groupId, r)

    def __cmd_res(self, group: int, r: dict):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DelDevFrGroupRsp",
            "GroupID": group,
            "Devices": []
        }
        for d in r.get("devices_success", []):
            res["Devices"].append({
                "Device": d,
                "Success": True
            })
        for d in r.get("devices_failure", []):
            res["Devices"].append({
                "Device": d,
                "Success": False
            })
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

