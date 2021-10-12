import asyncio
import time
from Controllers.RdHc import RdHc
import threading
from Database.Db import Db
import logging
from logging.handlers import TimedRotatingFileHandler
from HcServices.Mqtt import Mqtt
from Handler.MqttDataHandler import MqttDataHandler
import os


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


mqtt = Mqtt(logger)
mqtt.connect()
mqttHandler = MqttDataHandler(logger, mqtt)

db = Db()
db.init()

hc = RdHc(logger, mqtt, mqttHandler)

hc.hc_add_basic_info_to_db()
hc.hc_report_network_info()
hc.hc_update_devices_online_status_to_global_dict()
hc.hc_load_devices_heartbeat_to_global_dict()

async def main():
    await hc.run()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
