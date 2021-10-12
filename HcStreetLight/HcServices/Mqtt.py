import paho.mqtt.client as mqtt
import Constants.Constant as Const
import logging
import threading
import socket
from Constracts.ITransport import ITransport


class MqttConfig:
    host: str
    port: int
    qos: int
    keep_alive: int
    username: str
    password: str

    def __init__(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.host = ip
        self.port = Const.MQTT_PORT
        self.qos = Const.MQTT_QOS
        self.keep_alive = Const.MQTT_KEEP_ALIVE
        self.username = Const.MQTT_USER
        self.password = Const.MQTT_PASS


class Mqtt(ITransport):
    __mqttConfig: MqttConfig
    __client: mqtt.Client
    __logger: logging.Logger
    __lock: threading.Lock

    def __init__(self, log: logging.Logger):
        super().__init__()
        self.__logger = log
        self.__mqttConfig = MqttConfig()
        self.__client = mqtt.Client()
        self.__lock = threading.Lock()

    def __on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        topic = msg.topic
        item = {"topic": topic, "msg": message}
        self.receive_data_queue.put(item)
        return

    def __on_connect(self, client, userdata, flags, rc):
        self.__client.subscribe(topic=Const.MQTT_CLOUD_TO_DEVICE_REQUEST_TOPIC, qos=self.__mqttConfig.qos)
        self.__client.subscribe(topic=Const.MQTT_DEVICE_TO_CLOUD_RESPONSE_TOPIC, qos=self.__mqttConfig.qos)

    def send(self, destination, send_data):
        self.__client.publish(destination, payload=send_data, qos=Const.MQTT_QOS)

    def disconnect(self):
        self.__client.disconnect()

    def connect(self):
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(username=self.__mqttConfig.username, password=self.__mqttConfig.password)
        try:
            self.__client.connect("broker.mqttdashboard.com", self.__mqttConfig.port)
            self.__client.loop_start()
        except Exception as err:
            self.__logger.error(f"Exception in connect to mqtt: {err}")
            print(f"Exception in connect to mqtt: {err}")

    def reconnect(self):
        pass

    def receive(self):
        pass

    def is_readable(self):
        pass
