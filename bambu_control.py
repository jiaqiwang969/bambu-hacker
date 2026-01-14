#!/usr/bin/env python3
"""
Bambu Lab H2S 打印机控制脚本
"""

import json
import ssl
import time
import paho.mqtt.client as mqtt

# 打印机配置
PRINTER_IP = "192.168.31.58"
PRINTER_PORT = 8883  # MQTT over TLS
USERNAME = "bblp"
ACCESS_CODE = "5c910619"

# 重要：需要打印机序列号
# 在打印机屏幕上查看：设置 -> 设备 -> 序列号
# 如果不知道，先留空，脚本会尝试从消息中获取
SERIAL = None

# 序列号计数器
sequence_id = 0

def get_sequence_id():
    global sequence_id
    sequence_id += 1
    return str(sequence_id)

# MQTT 回调函数
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ 连接成功!")
        # 订阅所有 topic 来发现序列号
        client.subscribe("#")
        print("✓ 已订阅所有 topic")
    else:
        print(f"✗ 连接失败，错误码: {rc}")

def on_message(client, userdata, msg):
    global SERIAL
    try:
        topic = msg.topic
        print(f"\n收到消息 [topic: {topic}]")

        # 从 topic 中提取序列号
        if topic.startswith("device/") and "/report" in topic:
            parts = topic.split("/")
            if len(parts) >= 2 and SERIAL is None:
                SERIAL = parts[1]
                print(f"✓ 发现序列号: {SERIAL}")

        payload = json.loads(msg.payload.decode())
        # 只打印关键信息
        if "print" in payload:
            p = payload["print"]
            if "gcode_state" in p:
                print(f"  状态: {p.get('gcode_state')}")
            if "nozzle_temper" in p:
                print(f"  喷头温度: {p.get('nozzle_temper')}°C")
            if "bed_temper" in p:
                print(f"  热床温度: {p.get('bed_temper')}°C")
            if "mc_percent" in p:
                print(f"  进度: {p.get('mc_percent')}%")
        else:
            # 打印完整消息（截断）
            msg_str = json.dumps(payload, ensure_ascii=False)
            if len(msg_str) > 200:
                print(f"  {msg_str[:200]}...")
            else:
                print(f"  {msg_str}")
    except Exception as e:
        print(f"解析错误: {e}")
        print(f"原始消息: {msg.payload[:100]}")

def on_disconnect(client, userdata, disconnect_flags, rc, properties=None):
    print(f"断开连接，代码: {rc}")

# 创建 MQTT 客户端
def create_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USERNAME, ACCESS_CODE)

    # SSL 配置
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(ssl_context)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    return client

# 发送命令
def send_command(client, command_json):
    global SERIAL
    if SERIAL is None:
        print("错误: 序列号未知，请等待自动发现或手动设置")
        return

    topic = f"device/{SERIAL}/request"
    payload = json.dumps(command_json)
    result = client.publish(topic, payload)
    print(f"发送到 {topic}: {payload[:100]}...")

# 常用命令
def cmd_get_version(client):
    """获取版本信息"""
    cmd = {
        "info": {
            "command": "get_version",
            "sequence_id": get_sequence_id()
        }
    }
    send_command(client, cmd)

def cmd_push_all(client):
    """请求推送所有状态"""
    cmd = {
        "pushing": {
            "command": "pushall",
            "sequence_id": get_sequence_id()
        }
    }
    send_command(client, cmd)

def cmd_light_on(client):
    """开灯"""
    cmd = {
        "system": {
            "command": "ledctrl",
            "led_node": "chamber_light",
            "led_mode": "on",
            "sequence_id": get_sequence_id(),
            "led_on_time": 500,
            "led_off_time": 500,
            "loop_times": 1,
            "interval_time": 1000
        }
    }
    send_command(client, cmd)

def cmd_light_off(client):
    """关灯"""
    cmd = {
        "system": {
            "command": "ledctrl",
            "led_node": "chamber_light",
            "led_mode": "off",
            "sequence_id": get_sequence_id(),
            "led_on_time": 500,
            "led_off_time": 500,
            "loop_times": 1,
            "interval_time": 1000
        }
    }
    send_command(client, cmd)

def cmd_gcode(client, gcode):
    """发送 G-code"""
    cmd = {
        "print": {
            "command": "gcode_line",
            "param": gcode,
            "sequence_id": get_sequence_id()
        }
    }
    send_command(client, cmd)

def cmd_home(client):
    """回原点"""
    cmd_gcode(client, "G28")

# 主程序
if __name__ == "__main__":
    print("=" * 50)
    print("Bambu Lab H2S 控制脚本")
    print("=" * 50)
    print(f"目标: {PRINTER_IP}:{PRINTER_PORT}")
    if SERIAL:
        print(f"序列号: {SERIAL}")
    else:
        print("序列号: 等待自动发现...")
    print()

    client = create_client()

    try:
        print("正在连接...")
        client.connect(PRINTER_IP, PRINTER_PORT, 60)
        client.loop_start()

        # 等待连接和序列号发现
        print("等待打印机响应...")
        time.sleep(3)

        if SERIAL:
            # 请求完整状态
            print("\n请求打印机状态...")
            cmd_push_all(client)
            time.sleep(2)

        # 交互菜单
        print("\n" + "=" * 50)
        print("可用命令:")
        print("  1 - 获取状态 (pushall)")
        print("  2 - 开灯")
        print("  3 - 关灯")
        print("  4 - 回原点 (G28)")
        print("  v - 获取版本")
        print("  g <gcode> - 发送 G-code")
        print("  q - 退出")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n输入命令: ").strip()
            except EOFError:
                break

            if cmd == "q":
                break
            elif cmd == "1":
                cmd_push_all(client)
            elif cmd == "2":
                cmd_light_on(client)
            elif cmd == "3":
                cmd_light_off(client)
            elif cmd == "4":
                cmd_home(client)
            elif cmd == "v":
                cmd_get_version(client)
            elif cmd.startswith("g "):
                gcode = cmd[2:].strip()
                cmd_gcode(client, gcode)
            elif cmd:
                print("未知命令")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n中断")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.loop_stop()
        client.disconnect()
        print("已断开连接")
