from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import uuid
from sqlalchemy import and_, bindparam
import threading


class ControlDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")

        mqttReceiveCommandResponse = {
            "RQI": rqi
        }

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC,
                       json.dumps(mqttReceiveCommandResponse))

        devices_control_list = data.get("Device", [])
        groups_control_list = data.get("groups", [])

        devices_property = []

        # with threading.Lock():
        #     for g in groups_control_list:
        #         rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
        #             db.Table.GroupDeviceMappingTable.c.GroupId == g["group"]
        #         )
        #         if g["Type"] == 0:
        #             for r in rel:
        #                 devices_control_list.append(r["DeviceAddress"])
        #         if g["Type"] == 1:
        #             for r in rel:
        #                 if r["Number"] % 2 == 1:
        #                     devices_control_list.append(r["DeviceAddress"])
        #         if g["Type"] == 2:
        #             for r in rel:
        #                 if r["Number"] % 2 == 0:
        #                     devices_control_list.append(r["DeviceAddress"])
        unique_devices_control_list = set(devices_control_list)
        for d in unique_devices_control_list:
            if data.get("DIM") is not None:
                device_dim_property = {
                    "b_DeviceAddress": d,
                    "b_PropertyId": Const.PROPERTY_DIM_ID,
                    "b_PropertyValue": data.get("DIM")
                }
                devices_property.append(device_dim_property)

            if data.get("Relay") is not None:
                device_relay_property = {
                    "b_DeviceAddress": d,
                    "b_PropertyId": Const.PROPERTY_RELAY_ID,
                    "b_PropertyValue": data.get("Relay")
                }
                devices_property.append(device_relay_property)

        with threading.Lock():
            if devices_property:
                db.Services.DevicePropertyService.UpdateManyDevicePropertyMappingCustomByConditionType1(
                    devices_property)

        for d in devices_control_list:
            if data.get("DIM") is not None and data.get("Relay") is not None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlDevice",
                    "Device": d,
                    "Relay": data.get("Relay"),
                    "DIM": data.get("DIM")
                }
            elif data.get("DIM") is None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlDevice",
                    "Device": d,
                    "Relay": data.get("Relay"),
                    "DIM": -1
                }
            elif data.get("Relay") is None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlDevice",
                    "Device": d,
                    "Relay": -1,
                    "DIM": data.get("DIM")
                }

            self.addControlQueue(cmd_send_to_device)

        for g in groups_control_list:
            if data.get("DIM") is not None and data.get("Relay") is not None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlGroup",
                    "group": g.get("group"),
                    "Type": g.get("Type"),
                    "Relay": data.get("Relay"),
                    "DIM": data.get("DIM")
                }
            elif data.get("DIM") is None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlGroup",
                    "group": g.get("group"),
                    "Type": g.get("Type"),
                    "Relay": data.get("Relay"),
                    "DIM": -1
                }
            elif data.get("Relay") is None:
                cmd_send_to_device = {
                    "TYPCMD": "ControlGroup",
                    "group": g.get("group"),
                    "Type": g.get("Type"),
                    "Relay": -1,
                    "DIM": data.get("DIM")
                }
            self.addControlQueue(cmd_send_to_device)

        self.send_ending_cmd(self.addControlQueue)
        self.waiting_for_handler_cmd()
