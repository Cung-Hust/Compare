import json
import logging
import Constants.Constant as Const
from Constracts.IHandler import IHandler
from Constracts.ITransport import ITransport
from GlobalVariables.GlobalVariables import GlobalVariables
import threading
import uuid
from Database.Db import Db


class DeviceDataHandler(IHandler):
    __logger: logging.Logger
    __mqtt: ITransport
    __globalVariables = GlobalVariables()

    def __init__(self,  log: logging.Logger, mqtt: ITransport):
        self.__logger = log
        self.__mqtt = mqtt

    def handler(self, item):
        print(f"data recive from respnse buffer {item}")
        try:
            json_data = json.loads(item)
            cmd = json_data.get("TYPCMD")
            switcher = {
                "DeviceInfo": self.device_info,
                "End": self.end,
                "DeviceReport": self.device_report,
                "PingDeviceRsp": self.ping_device_rsp,
            }
            func = switcher.get(cmd)
            func(json_data)
        except:
            print("error when handler response buffer data")

    def device_info(self, data):
        db = Db()
        devices = data.get("Devices")
        for d in devices:
            update_data = {
                "FirmwareVersion": d.get("FirmVer"),
                'Longitude': d.get("GPS").get("Lat"),
                'Latitude': d.get("GPS").get("Long"),
                'TXPower': d.get("TXPower"),
            }
            db.Services.DeviceService.UpdateDeviceByCondition(
                db.Table.DeviceTable.c.DeviceAddress == d.get(
                    "Device"), update_data
            )

    def end(self, data):
        with threading.Lock():
            self.__globalVariables.on_uart_cmd_processing = False
        print("cmd handler end")

    def device_report(self, data):
        cmd_rsp = {
            "RQI": str(uuid.uuid4())
        }
        cmd_rsp.update(data)
        self.__mqtt.send(
            Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(cmd_rsp))
        # db = Db()
        # gateway_data_update = {
        #     'Minute': data.get("Minute"),
        #     'KWH': data.get("KWh"),
        # }
        # db.Services.GatewayService.UpdateGatewayById(
        #     Const.GATEWAY_ID, gateway_data_update)
        # devices = data.get("Devices")
        # for d in devices:
        #     update_data = {
        #         'KWH': d.get("KWh"),
        #         'ActiveTime': d.get("Minute"),
        #     }
        #     db.Services.DeviceService.UpdateDeviceByCondition(
        #         db.Table.DeviceTable.c.DeviceAddress == d.get(
        #             "Device"), update_data
        #     )

    def ping_device_rsp(self, data):
        cmd_rsp = {
            "RQI": str(uuid.uuid4()),
            "TYPCMD": data.get("TYPCMD"),
            "Device": data.get("Device"),
            "Sucess": data.get("Success"),
        }
        self.__mqtt.send(
            Const.MQTT_CLOUD_TO_DEVICE_RESPONSE_TOPIC, json.dumps(cmd_rsp))
