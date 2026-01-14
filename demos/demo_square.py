#!/usr/bin/env python3
"""
安全绘制正方形测试
在热床上方安全高度绘制空中正方形（不接触热床）

安全措施：
1. 先复位 (G28) 确保位置准确
2. Z 轴抬高到安全高度
3. 每步都有确认
4. 可随时 Ctrl+C 中断
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bambu_h2s import BambuClient, BambuCommands

PRINTER_IP = "192.168.31.58"
ACCESS_CODE = "5c910619"

# ============================================
# 安全参数 - 可根据需要调整
# ============================================
SAFE_Z_HEIGHT = 50      # 安全高度 50mm（远离热床）
SQUARE_SIZE = 30        # 正方形边长 30mm
CENTER_X = 128          # H2S 热床中心 X (256/2)
CENTER_Y = 128          # H2S 热床中心 Y (256/2)
MOVE_SPEED = 2000       # 移动速度 mm/min (较慢，便于观察)


def confirm(msg):
    """确认步骤"""
    print()
    response = input(f"⚠️  {msg} (y=继续 / n=取消): ").strip().lower()
    if response != 'y':
        print("❌ 用户取消操作")
        return False
    return True


def wait_with_countdown(seconds, msg="等待"):
    """带倒计时的等待"""
    print(f"   {msg}...", end="", flush=True)
    for i in range(seconds, 0, -1):
        print(f" {i}", end="", flush=True)
        time.sleep(1)
    print(" ✓")


def draw_square_in_air():
    """在空中绘制正方形轨迹"""

    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "        安全空中正方形绘制测试".center(50) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    print("┌─────────────────────────────────────────────────────────┐")
    print("│  ⚠️  安全说明                                           │")
    print("│                                                         │")
    print(f"│  • Z 高度: {SAFE_Z_HEIGHT}mm (远离热床，在空中运动)              │")
    print(f"│  • 正方形: {SQUARE_SIZE}mm × {SQUARE_SIZE}mm (小范围测试)              │")
    print(f"│  • 位置: 热床中心 ({CENTER_X}, {CENTER_Y})                      │")
    print("│  • 不挤出耗材，仅移动喷头轨迹                           │")
    print("│  • 随时可按 Ctrl+C 紧急中断                             │")
    print("└─────────────────────────────────────────────────────────┘")
    print()

    # 计算正方形四个角的坐标
    half = SQUARE_SIZE / 2
    corners = [
        (CENTER_X - half, CENTER_Y - half),  # 左下 (起点)
        (CENTER_X + half, CENTER_Y - half),  # 右下
        (CENTER_X + half, CENTER_Y + half),  # 右上
        (CENTER_X - half, CENTER_Y + half),  # 左上
    ]

    print("📐 正方形顶点坐标:")
    print(f"   ┌─────────────────────────────┐")
    print(f"   │  角4 ({corners[3][0]},{corners[3][1]}) ──── 角3 ({corners[2][0]},{corners[2][1]})  │")
    print(f"   │       │              │       │")
    print(f"   │       │    中心      │       │")
    print(f"   │       │  ({CENTER_X},{CENTER_Y})   │       │")
    print(f"   │       │              │       │")
    print(f"   │  角1 ({corners[0][0]},{corners[0][1]}) ──── 角2 ({corners[1][0]},{corners[1][1]})  │")
    print(f"   │      (起点)                  │")
    print(f"   └─────────────────────────────┘")
    print()

    # 第一次确认
    if not confirm("确认已阅读安全说明，热床上无障碍物？"):
        return

    # 连接打印机
    print()
    print("🔌 正在连接打印机...")

    client = BambuClient(PRINTER_IP, ACCESS_CODE)

    def on_msg(topic, payload):
        if "print" in payload:
            p = payload["print"]
            if "gcode_state" in p and p["gcode_state"] != "IDLE":
                print(f"   📡 状态变化: {p['gcode_state']}")

    client.on_message(on_msg)

    if not client.connect():
        print("❌ 连接失败!")
        return

    print(f"✅ 已连接")
    print(f"   序列号: {client.serial}")

    cmd = BambuCommands(client)

    # 获取当前状态
    print()
    print("📊 获取打印机状态...")
    cmd.push_all()
    time.sleep(2)

    state = client.state
    if state:
        print(f"   当前状态: {state.get('gcode_state', 'unknown')}")
        print(f"   喷嘴温度: {state.get('nozzle_temper', 'unknown')}°C")
        print(f"   热床温度: {state.get('bed_temper', 'unknown')}°C")

    # 检查是否空闲
    if state.get('gcode_state') != 'IDLE':
        print()
        print("❌ 打印机不在空闲状态，无法执行测试!")
        client.disconnect()
        return

    try:
        # ============================================
        # 步骤 1: 复位
        # ============================================
        print()
        print("━" * 60)
        print("步骤 1/5: 复位 (G28)")
        print("━" * 60)
        print("   将执行 G28 命令，所有轴回原点")

        if not confirm("开始复位？"):
            client.disconnect()
            return

        print("   🏠 执行 G28 回原点...")
        cmd.gcode_line("G28")
        wait_with_countdown(15, "等待复位完成")

        # ============================================
        # 步骤 2: 抬升到安全高度
        # ============================================
        print()
        print("━" * 60)
        print(f"步骤 2/5: 抬升到安全高度 Z={SAFE_Z_HEIGHT}mm")
        print("━" * 60)

        if not confirm(f"将 Z 轴抬升到 {SAFE_Z_HEIGHT}mm？"):
            client.disconnect()
            return

        print(f"   ⬆️  抬升 Z 轴到 {SAFE_Z_HEIGHT}mm...")
        cmd.gcode_line(f"G1 Z{SAFE_Z_HEIGHT} F1000")
        wait_with_countdown(5, "等待抬升完成")

        # ============================================
        # 步骤 3: 移动到起始点
        # ============================================
        print()
        print("━" * 60)
        print(f"步骤 3/5: 移动到起始点")
        print("━" * 60)

        x0, y0 = corners[0]
        print(f"   目标: X={x0}, Y={y0} (左下角)")

        if not confirm("移动到起始点？"):
            client.disconnect()
            return

        print(f"   ➡️  移动到 X={x0}, Y={y0}...")
        cmd.gcode_line(f"G1 X{x0} Y{y0} F{MOVE_SPEED}")
        wait_with_countdown(4, "等待移动完成")

        # ============================================
        # 步骤 4: 绘制正方形
        # ============================================
        print()
        print("━" * 60)
        print("步骤 4/5: 绘制正方形")
        print("━" * 60)
        print("   将依次移动到 4 个角点，形成正方形轨迹")

        if not confirm("开始绘制正方形？"):
            client.disconnect()
            return

        corner_names = ["右下", "右上", "左上", "左下(回起点)"]
        for i, (x, y) in enumerate(corners[1:] + [corners[0]]):
            print(f"   📍 边 {i+1}/4: 移动到{corner_names[i]} X={x}, Y={y}")
            cmd.gcode_line(f"G1 X{x} Y{y} F{MOVE_SPEED}")
            wait_with_countdown(2, "移动中")

        print()
        print("   ✅ 正方形绘制完成!")

        # ============================================
        # 步骤 5: 回到中心
        # ============================================
        print()
        print("━" * 60)
        print("步骤 5/5: 回到中心位置")
        print("━" * 60)

        print(f"   🎯 移动到中心 X={CENTER_X}, Y={CENTER_Y}...")
        cmd.gcode_line(f"G1 X{CENTER_X} Y{CENTER_Y} F{MOVE_SPEED}")
        wait_with_countdown(3, "移动中")

        # 完成
        print()
        print("╔" + "═" * 58 + "╗")
        print("║" + "        ✅ 测试完成!".center(52) + "║")
        print("╚" + "═" * 58 + "╝")
        print()
        print("喷头已在空中完成正方形轨迹运动。")
        print()

    except KeyboardInterrupt:
        print()
        print("⚠️  用户中断! 正在停止...")
        # 尝试停止运动
        try:
            cmd.gcode_line("M410")  # 紧急停止
        except:
            pass
        print("已发送停止命令")

    finally:
        client.disconnect()
        print("🔌 已断开连接")


if __name__ == "__main__":
    draw_square_in_air()
