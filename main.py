import asyncio
import time
from Controllers.RdHc import RdHc
import threading
from Database.Db import Db
import logging
from logging.handlers import TimedRotatingFileHandler
from HcServices.Mqtt import Mqtt, MqttConfig
from Handler.MqttDataHandler import MqttDataHandler
import os
from ctypes import *
import Constants.Constant as Const
from Handler.DeviceDataHandler import DeviceDataHandler
import socket

lib = cdll.LoadLibrary("/root/libHC_Riim_Cpp.so")

file_dir = os.path.dirname(__file__)

logging_handler = logging.handlers.TimedRotatingFileHandler(filename=file_dir + '/Logging/runtime.log', when="MIDNIGHT",
                                                            backupCount=4)
logging_formatter = logging.Formatter(fmt=(
    '%(asctime)s:\t'
    '%(levelname)s:\t'
    '%(filename)s:'
    '%(funcName)s():'
    '%(lineno)d\t'
    '%(message)s'
))
logger = logging.getLogger("my_log")
logging_handler.setFormatter(logging_formatter)
logger.addHandler(logging_handler)
logger.setLevel(logging.DEBUG)

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

mqttConfig = MqttConfig(
    host=ip, port=Const.MQTT_PORT, qos=Const.MQTT_QOS, keep_alive=Const.MQTT_KEEP_ALIVE,
    username=Const.MQTT_USER, password=Const.MQTT_PASS
)

mqtt = Mqtt(logger, mqttConfig)
mqtt.connect()
mqttHandler = MqttDataHandler(logger, mqtt)

deviceHandler = DeviceDataHandler(logger, mqtt)

db = Db()
db.init()

hc = RdHc(logger, mqtt, mqttHandler)

hc.hc_add_basic_info_to_db()
hc.hc_report_network_info()
hc.hc_update_devices_online_status_to_global_dict()
hc.hc_load_devices_heartbeat_to_global_dict()

# lib.C_start()


def thread_1():
    hc.hc_handler_mqtt_data()


def thread_2():
    asyncio.run(hc.hc_thread_report_interval())


def thread_3():
    while True:
        # b = c_char_p(lib.C_bufferPop(Const.RESPONSE_BUFFER)).value
        # rel = b.decode('utf-8')
        # if rel != "":
        #     deviceHandler.handler(rel)
        time.sleep(1)


def main():
    threads = list()

    threads.append(threading.Thread(target=thread_1, args=()))
    threads.append(threading.Thread(target=thread_2, args=()))
    threads.append(threading.Thread(target=thread_3, args=()))

    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == "__main__":
    main()
