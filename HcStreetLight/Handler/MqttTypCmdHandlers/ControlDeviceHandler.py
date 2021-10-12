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

        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        devices_control_list = data.get("Device", [])
        groups_control_list = data.get("groups", [])
        devices_property = []

        with threading.Lock():
            for g in groups_control_list:
                rel = db.Services.GroupDeviceMappingService.FindGroupDeviceMappingByCondition(
                    db.Table.GroupDeviceMappingTable.c.GroupId == g["group"]
                )
                if g["Type"] == 0:
                    for r in rel:
                        devices_control_list.append(r["DeviceAddress"])
                if g["Type"] == 1:
                    for r in rel:
                        if r["Number"] % 2 == 1:
                            devices_control_list.append(r["DeviceAddress"])
                if g["Type"] == 2:
                    for r in rel:
                        if r["Number"] % 2 == 0:
                            devices_control_list.append(r["DeviceAddress"])

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
            db.Services.DevicePropertyService.UpdateManyDevicePropertyMappingCustomByConditionType1(devices_property)
            
        self.__cmd_res(list(unique_devices_control_list))

    def __cmd_res(self, devs: list):
        db = Db()
        with threading.Lock():
            rel = db.Services.DeviceService.FindDeviceByCondition(
                db.Table.DeviceTable.c.DeviceAddress.in_(devs)
            )
        devices = rel.fetchall()

        with threading.Lock():
            rel2 = db.Services.DevicePropertyService.FindDevicePropertyMappingByCondition(
                db.Table.DevicePropertyMappingTable.c.DeviceAddress.in_(devs)
            )
        devicesPropertyMapping = rel2.fetchall()

        with threading.Lock():
            rel3 = db.Services.GatewayService.FindGatewayById(Const.GATEWAY_ID)
        gateway = dict(rel3.fetchone())

        res = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": "DeviceStatus",
            "Gateway": {
                "Temp": gateway.get("Temp"),
                "Lux": gateway.get("Lux"),
                "U": gateway.get("U"),
                "I": gateway.get("I"),
                "Cos": gateway.get("Cos"),
                "P": gateway.get("P"),
                "Minute": gateway.get("Minute"),
                "KWh": gateway.get("KWH"),
                "Scene": gateway.get("Scene"),
                "Relay": gateway.get("Relay_1") | gateway.get("Relay_2") | gateway.get("Relay_3") | gateway.get("Relay_4"),
                "Status": gateway.get("Status")
            },
            "Devices": []
        }

        temp = {}

        if len(devices) != 0:
            for device in devices:
                temp[device["DeviceAddress"]] = {
                    "Device": device["DeviceAddress"],
                    "Online": device["IsOnline"],
                    "Status": device["Status"],
                    "Scene": device["CurrentRunningScene"],
                    "Relay": bool(),
                    "DIM": 0,
                    "Temp": 0,
                    "Lux": 0,
                    "U": 0,
                    "I": 0,
                    "Cos": 0,
                    "P": 0,
                    "KWh": device['KWH']
                }

        if len(devicesPropertyMapping) != 0:
            for devicePropertyMapping in devicesPropertyMapping:
                r = devicePropertyMapping
                if r["PropertyId"] == Const.PROPERTY_RELAY_ID:
                    if r["PropertyValue"] == 0:
                        temp[r["DeviceAddress"]]["Relay"] = False
                    if r["PropertyValue"] == 1:
                        temp[r["DeviceAddress"]]["Relay"] = True
                    continue
                if r["PropertyId"] == Const.PROPERTY_DIM_ID:
                    temp[r["DeviceAddress"]]["DIM"] = int(r["PropertyValue"])
                    continue
                if r["PropertyId"] == Const.PROPERTY_P_ID:
                    temp[r["DeviceAddress"]]["P"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_TEMP_ID:
                    temp[r["DeviceAddress"]]["Temp"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_LUX_ID:
                    temp[r["DeviceAddress"]]["Lux"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_U_ID:
                    temp[r["DeviceAddress"]]["U"] = r["PropertyValue"]
                    continue
                if r["PropertyId"] == Const.PROPERTY_I_ID:
                    temp[r["DeviceAddress"]]["I"] = r["PropertyValue"]
                    continue


        for t in temp:
            res["Devices"].append(temp[t])
        with threading.Lock():
            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
        self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))
