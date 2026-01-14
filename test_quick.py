#!/usr/bin/env python3
"""
快速功能验证测试
测试安全的、不会影响打印的命令
"""

import sys
import time
sys.path.insert(0, "/Users/jqwang/161-bambu-hacker")

from bambu_h2s import BambuClient, BambuCommands

PRINTER_IP = "192.168.31.58"
ACCESS_CODE = "5c910619"


def test_safe_commands():
    """测试安全命令（不会影响打印）"""
    print("=" * 60)
    print("Bambu H2S 安全功能测试")
    print("=" * 60)

    client = BambuClient(PRINTER_IP, ACCESS_CODE)

    results = []

    def on_msg(topic, payload):
        if "system" in payload and "result" in payload["system"]:
            results.append(("system", payload["system"]["result"]))
        elif "info" in payload:
            results.append(("info", "received"))

    client.on_message(on_msg)

    print("\n1. 连接测试...")
    if not client.connect():
        print("   ❌ 连接失败")
        return
    print(f"   ✅ 连接成功，序列号: {client.serial}")

    cmd = BambuCommands(client)
    time.sleep(1)

    # 测试列表
    tests = [
        ("获取状态 (push_all)", lambda: cmd.push_all()),
        ("获取版本 (get_version)", lambda: cmd.get_version()),
        ("开灯 (light_on)", lambda: cmd.light_on()),
        ("关灯 (light_off)", lambda: cmd.light_off()),
        ("闪烁 (light_flash)", lambda: cmd.light_flash(2)),
        ("关灯 (light_off)", lambda: cmd.light_off()),
    ]

    print("\n2. 功能测试...")
    passed = 0
    failed = 0

    for name, func in tests:
        print(f"\n   测试: {name}")
        results.clear()
        try:
            func()
            time.sleep(1)
            print(f"   ✅ 命令已发送")
            passed += 1
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            failed += 1

    # 测试状态读取
    print("\n3. 状态读取测试...")
    cmd.push_all()
    time.sleep(2)

    state = client.state
    if state:
        print(f"   ✅ 状态获取成功:")
        if "gcode_state" in state:
            print(f"      - 打印状态: {state['gcode_state']}")
        if "nozzle_temper" in state:
            print(f"      - 喷嘴温度: {state['nozzle_temper']}°C")
        if "bed_temper" in state:
            print(f"      - 热床温度: {state['bed_temper']}°C")
        passed += 1
    else:
        print("   ❌ 状态获取失败")
        failed += 1

    client.disconnect()

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)


if __name__ == "__main__":
    test_safe_commands()
