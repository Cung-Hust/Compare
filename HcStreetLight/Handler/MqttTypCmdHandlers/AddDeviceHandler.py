import uuid
from Constracts.IMqttTypeCmdHandler import IMqttTypeCmdHandler
from Constracts import ITransport
import logging
import Constants.Constant as Const
import json
from Database.Db import Db
import threading
from Helper.Random import Random


class AddDeviceHandler(IMqttTypeCmdHandler):
    def __init__(self, log: logging.Logger, mqtt: ITransport):
        super().__init__(log, mqtt)

    def handler(self, data):
        db = Db()
        rqi = data.get("RQI")
        mqttReceiveCommandResponse = {
            "RQI": rqi
        }
        self.mqtt.send(Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(mqttReceiveCommandResponse))

        r = Random()
        current_devices_list = []

        with threading.Lock():
            rel = db.Services.DeviceService.FindAllDevice()
        devices_record = rel.fetchall()
        for d in devices_record:
            current_devices_list.append(d["DeviceAddress"])
        devices_add = list(set(data.get("Device", [])) - set(current_devices_list))
        devices_same = list(set(data.get("Device", [])).intersection(current_devices_list))
        devices_data_add = []
        devices_property_mapping_add = []
        if devices_add:
            for d in devices_add:
                devices_data_add.append({
                    'DeviceAddress': d,
                    'Ip': "121212121212",
                    'NetKey': "",
                    'PanId_1': "",
                    'PanId_2': "",
                    'Longitude': str(r.random_int_value_with_range(0, 180)),
                    'Latitude': str(r.random_int_value_with_range(0, 180)),
                    'TXPower': r.random_int_value_with_range(0, 180),
                    'VMax': r.random_float_value_with_range(0, 180),
                    'VMin':r.random_float_value_with_range(0, 180),
                    'IMax': r.random_float_value_with_range(0, 10),
                    'IMin': r.random_float_value_with_range(0, 10),
                    'CosMax': r.random_float_value_with_range(0, 1),
                    'CosMin': r.random_float_value_with_range(0, 1),
                    'PMax': r.random_float_value_with_range(0, 180),
                    'PMin': r.random_float_value_with_range(0, 180),
                    'TMax': r.random_float_value_with_range(0, 180),
                    'TMin': r.random_float_value_with_range(0, 180),
                    'LMax': r.random_float_value_with_range(0, 180),
                    'LMin': r.random_float_value_with_range(0, 180),
                    'ActiveTime': r.random_int_value_with_range(0, 100),
                    'CurrentRunningScene': int(),
                    'Status': int(),
                    'IsOnline': False,
                    'IsSync': True,
                    'DimInit': r.random_int_value_with_range(0, 100),
                    'PRating': r.random_int_value_with_range(0, 100),
                    'KWH': r.random_int_value_with_range(0, 100),
                    'FirmwareVersion': "1.1",
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_RELAY_ID,
                    "PropertyValue": r.random_bool_value()
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_DIM_ID,
                    "PropertyValue": r.random_int_value_with_range(0, 100)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_TEMP_ID,
                    "PropertyValue": r.random_float_value_with_range(0, 100)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_LUX_ID,
                    "PropertyValue": r.random_float_value_with_range(0, 180)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_U_ID,
                    "PropertyValue": r.random_float_value_with_range(0, 180)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_I_ID,
                    "PropertyValue": r.random_float_value_with_range(0, 10)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_COS_ID,
                    "PropertyValue": r.random_float_value_with_range(0, 1)
                })
                devices_property_mapping_add.append({
                    "DeviceAddress": d,
                    "PropertyId": Const.PROPERTY_P_ID,
                    "PropertyValue":  r.random_float_value_with_range(0, 180)
                })
            with threading.Lock():
                db.Services.DeviceService.InsertMany(devices_data_add)
                db.Services.DevicePropertyService.InsertManyDevicePropertyMapping(devices_property_mapping_add)
        r = {
            "devices_same": devices_same,
            "devices_add": devices_add
        }
        # self.__cmd_res(r)

    def __cmd_res(self, r: dict):
        db = Db()
        for d in r["devices_add"]:
            res = {
                "RQI": str(uuid.uuid4()),
                "TYPCMD": "NewDevice",
                "Device": d,
                "GPS": {
                    "Lat": "0",
                    "Long": "0"
                },
                "TXPower": 0,
                "FirmVer": "1.1"
            }

            self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
            self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))
        with threading.Lock():
            rel = db.Services.DeviceService.FindDeviceByCondition(
                db.Table.DeviceTable.c.DeviceAddress.in_(r["devices_same"])
            )
        devices = rel.fetchall()
        for d in devices:
            res = {
                "RQI": str(uuid.uuid4()),
                "TYPCMD": "NewDevice",
                "Device": d["DeviceAddress"],
                "GPS": {
                    "Lat": d["Latitude"],
                    "Long": d["Longitude"]
                },
                "TXPower": d["TXPower"],
                "FirmVer": d["FirmwareVersion"]
            }
            with threading.Lock():
                self.globalVariable.mqtt_need_response_dict[res["RQI"]] = res
            self.mqtt.send(Const.MQTT_DEVICE_TO_CLOUD_REQUEST_TOPIC, json.dumps(res))

