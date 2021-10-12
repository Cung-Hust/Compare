import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading


class SetSceneHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        r = {}
        db = Db()

        mqttReceiveCommandResponse = {
            "RQI": data.get("RQI")
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        rel = db.Services.EventTriggerService.FindEventTriggerById(data.get("ID"))
        event = rel.fetchone()

        if event is None:
            r = self.__save_new_scene_to_db(data)

        if event is not None:
            self.__remove_all_event_data(data.get("ID"))
            r = self.__save_new_scene_to_db(data)

        # self.__cmd_res(data.get("ID"), r)

    def __save_new_scene_to_db(self, data) -> dict:
        db = Db()
        db.Services.EventTriggerService.InsertEventTrigger(
            {
                "EventTriggerId": data.get("ID"),
                "ScriptType": data.get("script_type"),
                "IsEnable": True,
                "ScheduleRaw": data.get("input_condition").get("schedule")
            }
        )
        self.__save_input_condition_to_db(data)
        rel = self.__save_output_action_to_db(data)
        return rel

    def __save_input_condition_to_db(self, data):
        db = Db()
        devices_input_condition = data.get("input_condition").get("device_condition", [])
        if not devices_input_condition:
            return

        devices_mapping_input_insert = []
        devices_setup_input_insert = []

        for device_input_condition in devices_input_condition:
            device_mapping_input_insert = {
                "EventTriggerId": data["ID"],
                "DeviceAddress": device_input_condition["Device"],
            }

            device_setup_input_insert = {
                "EventTriggerId": data["ID"],
                "DeviceAddress": device_input_condition["Device"],
                "PropertyId": device_input_condition["condition"]["attribute"],
                "PropertyValue": device_input_condition["condition"]["value"],
                "Operation": device_input_condition["condition"]["operation"]
            }
            devices_setup_input_insert.append(device_setup_input_insert)
            devices_mapping_input_insert.append(device_mapping_input_insert)

        db.Services.EventTriggerInputDeviceMappingService.InsertManyEventTriggerInputDeviceMapping(
            devices_mapping_input_insert)
        db.Services.EventTriggerInputDeviceSetupValueService.InsertManyEventTriggerInputDeviceSetupValue(
            devices_setup_input_insert
        )

    def __save_output_action_to_db(self, data) -> dict:
        db = Db()

        devices_output_action = data.get("execute").get("device_action", [])
        devices_output_mapping = []
        devices_output_setup_value = []
        devices_success_list = []

        groups_output_action = data.get("execute").get("group_action", [])
        groups_output_mapping = []
        groups_output_setup_value = []
        groups_success_list = []

        for device_output_action in devices_output_action:
            action = device_output_action.get("action")
            device_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            device_output_dim_setup_value = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "PropertyId": Const.PROPERTY_DIM_ID,
                "PropertyValue": action.get("DIM")
            }
            device_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "DeviceAddress": device_output_action.get("Device"),
                "IsEnable": True
            }
            devices_output_setup_value.append(device_output_relay_setup_value)
            devices_output_setup_value.append(device_output_dim_setup_value)
            devices_output_mapping.append(device_output_mapping)
            devices_success_list.append(device_output_action.get("Device"))

        for group_output_action in groups_output_action:
            action = group_output_action.get("action")
            group_output_relay_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_RELAY_ID,
                "PropertyValue": action.get("Relay")
            }
            group_output_dim_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_DIM_ID,
                "PropertyValue": action.get("DIM")
            }
            group_output_type_setup_value = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "PropertyId": Const.PROPERTY_TYPE_ID,
                "PropertyValue": action.get("Type")
            }
            group_output_mapping = {
                "EventTriggerId": data.get("ID"),
                "GroupId": group_output_action.get("GroupId"),
                "IsEnable": True
            }
            groups_output_setup_value.append(group_output_relay_setup_value)
            groups_output_setup_value.append(group_output_dim_setup_value)
            groups_output_setup_value.append(group_output_type_setup_value)

            groups_output_mapping.append(group_output_mapping)
            groups_success_list.append(group_output_action.get("GroupId"))

        if devices_output_mapping:
            db.Services.EventTriggerOutputDeviceMappingService.InsertManyEventTriggerOutputDeviceMapping(
                devices_output_mapping
            )
        if devices_output_setup_value:
            db.Services.EventTriggerOutputDeviceSetupValueService.InsertManyEventTriggerOutputDeviceSetupValue(
                devices_output_setup_value
            )
        if groups_output_mapping:
            db.Services.EventTriggerOutputGroupMappingService.InsertManyEventTriggerOutputGroupMapping(
                groups_output_mapping
            )
        if groups_output_setup_value:
            db.Services.EventTriggerOutputGroupSetupValueService.InsertEventTriggerOutputGroupSetupValue(
                groups_output_setup_value
            )
        return {
            "device_success": devices_success_list,
            "device_failure": [],
            "group_success": groups_success_list,
            "group_failure": []
        }

    def __remove_all_event_data(self, event: int):
        db = Db()
        db.Services.EventTriggerInputDeviceSetupValueService.RemoveEventTriggerInputDeviceSetupValueByCondition(
            db.Table.EventTriggerInputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerInputDeviceMappingService.RemoveEventTriggerInputDeviceMappingByCondition(
            db.Table.EventTriggerInputDeviceMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputDeviceMappingService.RemoveEventTriggerOutputDeviceMappingByCondition(
            db.Table.EventTriggerOutputDeviceMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputDeviceSetupValueService.RemoveEventTriggerOutputDeviceSetupValueByCondition(
            db.Table.EventTriggerOutputDeviceSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputGroupMappingService.RemoveEventTriggerOutputGroupMappingByCondition(
            db.Table.EventTriggerOutputGroupMappingTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerOutputGroupSetupValueService.RemoveEventTriggerOutputGroupSetupValueByCondition(
            db.Table.EventTriggerOutputGroupSetupValueTable.c.EventTriggerId == event
        )
        db.Services.EventTriggerService.RemoveEventTriggerByCondition(
            db.Table.EventTriggerTable.c.EventTriggerId == event
        )

    def __cmd_res(self, scene: int, r: dict):
        res = {"RQI": str(uuid.uuid4()), "TYPCMD": "SetSceneRsp", "ID": scene, "Devices": [], "Groups": []}
        for d in r.get("device_success", []):
            res["Devices"].append({
                "Device": d,
                "Success": True
            })
        for d in r.get("device_failure", []):
            res["Devices"].append({
                "Device": d,
                "Success": False
            })
        for g in r.get("group_success", []):
            res["Groups"].append({
                "GroupId": g,
                "Success": True
            })
        for g in r.get("group_failure", []):
            res["Groups"].append({
                "GroupId": g,
                "Success": False
            })
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

