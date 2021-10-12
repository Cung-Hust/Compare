import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
from sqlalchemy import and_
import threading


class DelDeviceInSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI")
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices_delete_list = data.get("Device", [])
        groups_delete_list = data.get("group", [])

        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            and_(
                db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputDeviceMappingTable.c.DeviceAddress.in_(devices_delete_list)
            )
        )

        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            and_(
                db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputDeviceSetupValueTable.c.DeviceAddress.in_(devices_delete_list)
            )
        )

        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            and_(
                db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputGroupMappingTable.c.GroupId.in_(groups_delete_list)
            )
        )

        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            and_(
                db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == data.get("ID"),
                db.Table.EventTriggerOutputGroupSetupValueTable.c.GroupId.in_(groups_delete_list)
            )
        )

        # self.__cmd_res(data.get("ID"), devices_delete_list, groups_delete_list)

    def __cmd_res(self, scene: int, devices: list, groups: list):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DelDeviceInSceneRsp",
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
