"""
Bambu Lab MQTT 客户端
"""

import json
import ssl
import time
import threading
from typing import Callable, Optional, Dict, Any
import paho.mqtt.client as mqtt


class BambuClient:
    """Bambu Lab 打印机 MQTT 客户端"""

    def __init__(
        self,
        ip: str,
        access_code: str,
        serial: Optional[str] = None,
        port: int = 8883,
        username: str = "bblp"
    ):
        self.ip = ip
        self.port = port
        self.username = username
        self.access_code = access_code
        self.serial = serial

        self._client: Optional[mqtt.Client] = None
        self._connected = False
        self._sequence_id = 0
        self._lock = threading.Lock()

        # 回调函数
        self._on_message_callback: Optional[Callable] = None
        self._on_connect_callback: Optional[Callable] = None
        self._on_disconnect_callback: Optional[Callable] = None

        # 状态存储
        self.state: Dict[str, Any] = {}
        self._last_response: Optional[Dict] = None
        self._response_event = threading.Event()

    def get_sequence_id(self) -> str:
        """获取递增的序列号"""
        with self._lock:
            self._sequence_id += 1
            return str(self._sequence_id)

    def connect(self, timeout: float = 10.0) -> bool:
        """连接到打印机"""
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.username_pw_set(self.username, self.access_code)

        # SSL 配置
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self._client.tls_set_context(ssl_context)

        # 设置回调
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        try:
            self._client.connect(self.ip, self.port, 60)
            self._client.loop_start()

            # 等待连接
            start = time.time()
            while not self._connected and (time.time() - start) < timeout:
                time.sleep(0.1)

            if self._connected:
                # 等待序列号发现
                if self.serial is None:
                    time.sleep(2)
                return True
            return False
        except Exception as e:
            print(f"连接错误: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """连接回调"""
        if rc == 0:
            self._connected = True
            # 订阅所有 topic
            client.subscribe("#")
            if self._on_connect_callback:
                self._on_connect_callback()
        else:
            print(f"连接失败，错误码: {rc}")

    def _on_message(self, client, userdata, msg):
        """消息回调"""
        try:
            topic = msg.topic

            # 从 topic 提取序列号
            if topic.startswith("device/") and "/report" in topic:
                parts = topic.split("/")
                if len(parts) >= 2 and self.serial is None:
                    self.serial = parts[1]

            payload = json.loads(msg.payload.decode())

            # 更新状态
            if "print" in payload:
                self.state.update(payload["print"])

            # 存储响应
            self._last_response = payload
            self._response_event.set()

            # 用户回调
            if self._on_message_callback:
                self._on_message_callback(topic, payload)

        except Exception as e:
            pass

    def _on_disconnect(self, client, userdata, disconnect_flags, rc, properties=None):
        """断开连接回调"""
        self._connected = False
        if self._on_disconnect_callback:
            self._on_disconnect_callback(rc)

    def publish(self, command: Dict[str, Any], wait_response: bool = False, timeout: float = 5.0) -> Optional[Dict]:
        """发送命令"""
        if not self._connected or self.serial is None:
            print("未连接或序列号未知")
            return None

        topic = f"device/{self.serial}/request"
        payload = json.dumps(command)

        if wait_response:
            self._response_event.clear()
            self._last_response = None

        self._client.publish(topic, payload)

        if wait_response:
            if self._response_event.wait(timeout):
                return self._last_response
            return None
        return {"status": "sent"}

    def on_message(self, callback: Callable):
        """设置消息回调"""
        self._on_message_callback = callback

    def on_connect(self, callback: Callable):
        """设置连接回调"""
        self._on_connect_callback = callback

    def on_disconnect(self, callback: Callable):
        """设置断开回调"""
        self._on_disconnect_callback = callback

    @property
    def is_connected(self) -> bool:
        return self._connected
