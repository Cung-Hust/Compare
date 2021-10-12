import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const
import sqlite3

def sql_delete(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()

class DelGwSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))
        event = data.get("ID")
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event
        )
        
        cmd = "DELETE FROM GatewayEventTrigger WHERE EventTriggerId = " + str(event)
        cmd = sql_delete(cmd)
        cmd = "DELETE FROM GatewayEventTriggerOutputRelay WHERE EventTriggerId = " + str(event)
        cmd = sql_delete(cmd)