import uuid
import threading
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
from Database.Db import Db
import logging
import json
import Constants.Constant as Const
import sqlite3


def sql_insert(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()

def sql_select(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    return cur.fetchall()
    con.close()


def sql_delete(cmd):
    con = sqlite3.connect('rd.sqlite')
    cur = con.cursor()

    # Insert a row of data
    cur.execute(cmd)
    con.commit()
    con.close()


class SetGwSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        cmd = "SELECT * FROM GatewayEventTrigger WHERE EventTriggerId = " + str(data.get('ID'))
        print(cmd)

        event = sql_select(cmd)
        print(event)

        if event is None:
            self.__save_new_scene_to_db(data)

        if event is not None:
            self.__remove_all_event_data(data.get("ID"))
            self.__save_new_scene_to_db(data)

    def __save_new_scene_to_db(self, data):
        # print("Hello")
        cmd = "INSERT INTO GatewayEventTrigger(EventTriggerId, ScheduleRaw, ScriptType, IsEnable) VALUES(" + \
               str(data.get('ID')) + ", '" + data.get('input_condition').get('schedule') + "', " + str(data.get('script_type')) + ", true)"
        print(cmd)
        sql_insert(cmd)
        self.__save_input_condition_to_db(data)
        self.__save_output_action_to_db(data)

    def __save_input_condition_to_db(self, data):
        db = Db()
        devices_input_condition = data.get("input_condition").get("condition", [])
        if not devices_input_condition:
            return

        devices_mapping_input_insert = []
        devices_setup_input_insert = []

        for device_input_condition in devices_input_condition:
            device_mapping_input_insert = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_input_condition.get("Device"),
            }

            device_setup_input_insert = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_input_condition.get("Device"),
                "PropertyId": device_input_condition.get("condition").get("attribute"),
                "PropertyValue": device_input_condition.get("condition").get("value"),
                "Operation": device_input_condition.get("condition").get("operation")
            }
            devices_setup_input_insert.append(device_setup_input_insert)
            devices_mapping_input_insert.append(device_mapping_input_insert)

        db.Services.EventTriggerInputDeviceMappingService.InsertManyEventTriggerInputDeviceMapping(
            devices_mapping_input_insert)
        db.Services.EventTriggerInputDeviceSetupValueService.InsertManyEventTriggerInputDeviceSetupValue(
            devices_setup_input_insert
        )

    def __save_output_action_to_db(self, data):
        output = data.get('execute')
        EventTriggerId =  data.get("ID")
        relay_1 = output.get('Relay_1')
        relay_2 = output.get('Relay_2')
        relay_3 = output.get('Relay_3')
        relay_4 = output.get('Relay_4')


        if relay_1 is not None:
            cmd = "INSERT OR REPLACE INTO GatewayEventTriggerOutputRelay VALUES(" + str(EventTriggerId) + ", 'Relay_1', " + str(relay_1) + ")"
            print(cmd)
            sql_insert(cmd)
        
        if relay_2 is not None:
            cmd = "INSERT OR REPLACE INTO GatewayEventTriggerOutputRelay VALUES(" + str(EventTriggerId) + ", 'Relay_2', " + str(relay_2) + ")"
            print(cmd)
            sql_insert(cmd)
        
        if relay_3 is not None:
            cmd = "INSERT OR REPLACE INTO GatewayEventTriggerOutputRelay VALUES(" + str(EventTriggerId) + ", 'Relay_3', " + str(relay_3) + ")"
            print(cmd)
            sql_insert(cmd)
        
        if relay_4 is not None:
            cmd = "INSERT OR REPLACE INTO GatewayEventTriggerOutputRelay VALUES(" + str(EventTriggerId) + ", 'Relay_4', " + str(relay_4) + ")"
            print(cmd)
            sql_insert(cmd)

    def __remove_all_event_data(self, event: int):
        db = Db()
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




