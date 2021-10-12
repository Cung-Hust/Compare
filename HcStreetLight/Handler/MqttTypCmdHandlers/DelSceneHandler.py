from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
import threading


class DelSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI")
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))
        event_delete = data.get("ID")
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == event_delete
        )
        db.Services.EventTriggerService.RemoveEventTriggerByCondition(
            db.Table.EventTriggerTable.c.EventTriggerId == event_delete
        )
        # self.__cmd_res(event_delete, True)

    def __cmd_res(self, event_id: int, success: bool):
        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DelSceneRsp",
            "ID": event_id,
            "Success": success
        }
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

