#!/usr/bin/env python3
"""
Bambu Lab H2S 完整功能测试程序
交互式测试所有 56 个命令
"""

import sys
import time
sys.path.insert(0, "/Users/jqwang/161-bambu-hacker")

from bambu_h2s import BambuClient, BambuCommands, BambuFTP

# 打印机配置
PRINTER_IP = "192.168.31.58"
ACCESS_CODE = "5c910619"


def print_menu():
    """打印主菜单"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Bambu Lab H2S 完整功能测试程序                      ║
╠══════════════════════════════════════════════════════════════╣
║  【打印控制】                    【温度控制】                  ║
║   1. stop     - 停止打印          11. bed_temp   - 热床温度   ║
║   2. pause    - 暂停打印          12. nozzle_temp- 喷嘴温度   ║
║   3. resume   - 恢复打印          13. chamber    - 腔室温度   ║
║   4. skip_obj - 跳过对象          14. refresh    - 刷新喷嘴   ║
║   5. clean_err- 清除错误                                      ║
║   6. gcode    - 发送G-code       【风扇控制】                  ║
║   7. gcode_f  - 执行G-code文件    21. fan        - 风扇速度   ║
║                                   22. airduct    - 风道模式   ║
║  【AMS 控制】                                                 ║
║   31. ams_change  - 换料         【打印选项】                  ║
║   32. ams_setting - 设置          41. speed      - 打印速度   ║
║   33. ams_filament- 耗材设置      42. option     - 打印选项   ║
║   34. ams_rfid    - 读RFID        43. extrude    - 挤出长度   ║
║   35. ams_ctrl    - AMS控制       44. anti_heat  - 防加热     ║
║   36. ams_dry     - 停止干燥                                  ║
║                                  【校准功能】                  ║
║  【摄像头控制】                    51. calibrate  - 综合校准   ║
║   61. cam_record  - 录制          52. ext_cali   - 挤出校准   ║
║   62. cam_lapse   - 延时摄影      53. flow_cali  - 流量校准   ║
║   63. cam_res     - 分辨率                                    ║
║                                  【轴控制】                    ║
║  【灯光控制】                      71. home       - 回原点     ║
║   81. light_on    - 开灯          72. center     - 回中心     ║
║   82. light_off   - 关灯          73. move       - 移动轴     ║
║   83. light_flash - 闪烁          74. extruder   - 选挤出机   ║
║                                                               ║
║  【系统命令】                     【X-Cam AI】                 ║
║   91. version     - 固件版本      101. xcam      - AI检测     ║
║   92. push_all    - 获取状态                                  ║
║   93. door        - 门检测       【FTP 文件】                  ║
║   94. cache       - 打印缓存      111. ftp_list  - 列出文件   ║
║   95. buzzer      - 关蜂鸣器      112. ftp_upload- 上传文件   ║
║                                                               ║
║   0. 退出    s. 显示状态    h. 帮助                           ║
╚══════════════════════════════════════════════════════════════╝
""")


def on_message(topic, payload):
    """消息回调"""
    if "print" in payload:
        p = payload["print"]
        info = []
        if "gcode_state" in p:
            info.append(f"状态:{p['gcode_state']}")
        if "nozzle_temper" in p:
            info.append(f"喷嘴:{p['nozzle_temper']}°C")
        if "bed_temper" in p:
            info.append(f"热床:{p['bed_temper']}°C")
        if "mc_percent" in p:
            info.append(f"进度:{p['mc_percent']}%")
        if info:
            print(f"  📊 {' | '.join(info)}")
    elif "system" in payload:
        s = payload["system"]
        if "result" in s:
            print(f"  ✓ 系统响应: {s.get('result')}")
    elif "info" in payload:
        print(f"  ℹ️ 信息: {payload['info']}")


def test_print_control(cmd: BambuCommands, choice: str):
    """测试打印控制命令"""
    if choice == "1":
        print("⚠️  确定要停止打印吗？(y/n): ", end="")
        if input().lower() == "y":
            cmd.stop()
            print("  → 已发送停止命令")
    elif choice == "2":
        cmd.pause()
        print("  → 已发送暂停命令")
    elif choice == "3":
        cmd.resume()
        print("  → 已发送恢复命令")
    elif choice == "4":
        objs = input("  输入要跳过的对象ID (逗号分隔): ")
        obj_list = [int(x.strip()) for x in objs.split(",") if x.strip()]
        cmd.skip_objects(obj_list)
        print(f"  → 已跳过对象: {obj_list}")
    elif choice == "5":
        cmd.clean_print_error()
        print("  → 已清除打印错误")
    elif choice == "6":
        gcode = input("  输入 G-code (如 G28, M104 S200): ")
        cmd.gcode_line(gcode)
        print(f"  → 已发送: {gcode}")
    elif choice == "7":
        path = input("  输入 G-code 文件路径: ")
        cmd.gcode_file(path)
        print(f"  → 已执行文件: {path}")


def test_temp_control(cmd: BambuCommands, choice: str):
    """测试温度控制命令"""
    if choice == "11":
        temp = int(input("  输入热床温度 (0-110): "))
        cmd.set_bed_temp(temp)
        print(f"  → 热床温度设为: {temp}°C")
    elif choice == "12":
        temp = int(input("  输入喷嘴温度 (0-300): "))
        cmd.set_nozzle_temp(temp)
        print(f"  → 喷嘴温度设为: {temp}°C")
    elif choice == "13":
        temp = int(input("  输入腔室温度 (0-60): "))
        cmd.set_chamber_temp(temp)
        print(f"  → 腔室温度设为: {temp}°C")
    elif choice == "14":
        cmd.refresh_nozzle()
        print("  → 已刷新喷嘴状态")


def test_fan_control(cmd: BambuCommands, choice: str):
    """测试风扇控制命令"""
    if choice == "21":
        print("  风扇索引: 0=部件冷却, 1=辅助, 2=腔室")
        fan = int(input("  输入风扇索引 (0-2): "))
        speed = int(input("  输入速度 (0-100): "))
        cmd.set_fan(fan, speed)
        print(f"  → 风扇{fan}速度设为: {speed}%")
    elif choice == "22":
        mode = int(input("  输入风道模式 (0-2): "))
        cmd.set_airduct(mode)
        print(f"  → 风道模式设为: {mode}")


def test_ams_control(cmd: BambuCommands, choice: str):
    """测试 AMS 控制命令"""
    if choice == "31":
        ams_id = int(input("  AMS ID (0-3): "))
        slot_id = int(input("  槽位 ID (0-3): "))
        cmd.ams_change_filament(ams_id, slot_id)
        print(f"  → 换料: AMS{ams_id} 槽位{slot_id}")
    elif choice == "32":
        cmd.ams_user_setting()
        print("  → 已发送 AMS 设置")
    elif choice == "33":
        ams_id = int(input("  AMS ID: "))
        slot_id = int(input("  槽位 ID: "))
        tray_type = input("  耗材类型 (PLA/ABS/PETG): ")
        cmd.ams_filament_setting(ams_id, slot_id, slot_id, tray_type)
        print(f"  → 已设置耗材: {tray_type}")
    elif choice == "34":
        ams_id = int(input("  AMS ID: "))
        slot_id = int(input("  槽位 ID: "))
        cmd.ams_get_rfid(ams_id, slot_id)
        print("  → 已请求 RFID 信息")
    elif choice == "35":
        print("  操作: resume/reset/pause/done/abort")
        action = input("  输入操作: ")
        cmd.ams_control(action)
        print(f"  → AMS 操作: {action}")
    elif choice == "36":
        cmd.ams_stop_dry()
        print("  → 已停止 AMS 干燥")


def test_print_options(cmd: BambuCommands, choice: str):
    """测试打印选项命令"""
    if choice == "41":
        print("  速度: 1=静音, 2=标准, 3=运动, 4=疯狂")
        level = int(input("  输入速度等级 (1-4): "))
        cmd.set_print_speed(level)
        print(f"  → 打印速度设为: {level}")
    elif choice == "42":
        cmd.set_print_option()
        print("  → 已发送打印选项")
    elif choice == "43":
        length = float(input("  输入挤出长度 (mm): "))
        cmd.set_extrusion_length(length)
        print(f"  → 挤出: {length}mm")
    elif choice == "44":
        enable = input("  启用防加热? (y/n): ").lower() == "y"
        cmd.set_anti_heating_mode(enable)
        print(f"  → 防加热模式: {'启用' if enable else '禁用'}")


def test_calibration(cmd: BambuCommands, choice: str):
    """测试校准命令"""
    if choice == "51":
        print("  校准选项 (可组合):")
        print("    1=振动, 2=床平整, 4=X-cam, 8=电机噪音")
        print("    16=喷嘴, 32=床, 64=夹紧位置, 127=全部")
        option = int(input("  输入选项值: "))
        cmd.calibration(option)
        print(f"  → 开始校准: {option}")
    elif choice == "52":
        tray_id = int(input("  托盘 ID: "))
        cmd.extrusion_cali(tray_id)
        print("  → 开始挤出量校准")
    elif choice == "53":
        tray_id = int(input("  托盘 ID: "))
        cmd.flowrate_cali(tray_id, "GFL99", "GFL99")
        print("  → 开始流量校准")


def test_camera(cmd: BambuCommands, choice: str):
    """测试摄像头命令"""
    if choice == "61":
        enable = input("  启用录制? (y/n): ").lower() == "y"
        cmd.camera_record(enable)
        print(f"  → 录制: {'启用' if enable else '禁用'}")
    elif choice == "62":
        enable = input("  启用延时摄影? (y/n): ").lower() == "y"
        cmd.camera_timelapse(enable)
        print(f"  → 延时摄影: {'启用' if enable else '禁用'}")
    elif choice == "63":
        res = input("  分辨率 (720p/1080p): ")
        cmd.camera_resolution(res)
        print(f"  → 分辨率设为: {res}")


def test_axis(cmd: BambuCommands, choice: str):
    """测试轴控制命令"""
    if choice == "71":
        cmd.home()
        print("  → 回原点 (G28)")
    elif choice == "72":
        cmd.back_to_center()
        print("  → 回中心")
    elif choice == "73":
        axis = input("  轴 (X/Y/Z/E): ").upper()
        direction = int(input("  方向 (1=正, -1=负): "))
        mode = int(input("  模式 (0=小步, 1=大步): "))
        cmd.move_axis(axis, direction, mode)
        print(f"  → 移动 {axis} 轴")
    elif choice == "74":
        idx = int(input("  挤出机索引: "))
        cmd.select_extruder(idx)
        print(f"  → 选择挤出机: {idx}")


def test_light(cmd: BambuCommands, choice: str):
    """测试灯光命令"""
    if choice == "81":
        cmd.light_on()
        print("  → 灯已开启")
    elif choice == "82":
        cmd.light_off()
        print("  → 灯已关闭")
    elif choice == "83":
        loops = int(input("  闪烁次数: "))
        cmd.light_flash(loops)
        print(f"  → 闪烁 {loops} 次")


def test_system(cmd: BambuCommands, choice: str):
    """测试系统命令"""
    if choice == "91":
        cmd.get_version()
        print("  → 已请求版本信息")
    elif choice == "92":
        cmd.push_all()
        print("  → 已请求所有状态")
    elif choice == "93":
        print("  门检测: 0=禁用, 1=警告, 2=暂停")
        config = int(input("  输入配置: "))
        cmd.set_door_detection(config)
        print(f"  → 门检测设为: {config}")
    elif choice == "94":
        enable = input("  启用打印缓存? (y/n): ").lower() == "y"
        cmd.set_print_cache(enable)
        print(f"  → 打印缓存: {'启用' if enable else '禁用'}")
    elif choice == "95":
        cmd.buzzer_off()
        print("  → 蜂鸣器已关闭")


def test_xcam(cmd: BambuCommands, choice: str):
    """测试 X-Cam 命令"""
    if choice == "101":
        print("  模块: printing_monitor / first_layer_inspector / buildplate_marker_detector")
        module = input("  输入模块名: ")
        enable = input("  启用? (y/n): ").lower() == "y"
        cmd.xcam_control(module, enable)
        print(f"  → X-Cam {module}: {'启用' if enable else '禁用'}")


def test_ftp(choice: str):
    """测试 FTP 功能"""
    ftp = BambuFTP(PRINTER_IP, ACCESS_CODE)

    if choice == "111":
        if ftp.connect():
            print("\n  文件列表:")
            files = ftp.list_files("/")
            for f in files:
                print(f"    {f}")
            ftp.disconnect()
    elif choice == "112":
        local_path = input("  本地文件路径: ")
        if ftp.connect():
            def progress(uploaded, total):
                pct = (uploaded / total) * 100
                print(f"\r  上传进度: {pct:.1f}%", end="")

            ftp.upload_file(local_path, progress_callback=progress)
            print()
            ftp.disconnect()


def main():
    """主程序"""
    print("=" * 60)
    print("Bambu Lab H2S 完整功能测试")
    print("=" * 60)
    print(f"目标: {PRINTER_IP}")
    print()

    # 连接
    client = BambuClient(PRINTER_IP, ACCESS_CODE)
    client.on_message(on_message)

    print("正在连接...")
    if not client.connect():
        print("连接失败!")
        return

    print(f"✓ 连接成功! 序列号: {client.serial}")

    # 创建命令对象
    cmd = BambuCommands(client)

    # 获取初始状态
    cmd.push_all()
    time.sleep(1)

    print_menu()

    try:
        while True:
            choice = input("\n命令> ").strip().lower()

            if choice == "0" or choice == "q":
                break
            elif choice == "h":
                print_menu()
            elif choice == "s":
                cmd.push_all()
                time.sleep(1)

            # 打印控制 1-7
            elif choice in ["1", "2", "3", "4", "5", "6", "7"]:
                test_print_control(cmd, choice)

            # 温度控制 11-14
            elif choice in ["11", "12", "13", "14"]:
                test_temp_control(cmd, choice)

            # 风扇控制 21-22
            elif choice in ["21", "22"]:
                test_fan_control(cmd, choice)

            # AMS 控制 31-36
            elif choice in ["31", "32", "33", "34", "35", "36"]:
                test_ams_control(cmd, choice)

            # 打印选项 41-44
            elif choice in ["41", "42", "43", "44"]:
                test_print_options(cmd, choice)

            # 校准 51-53
            elif choice in ["51", "52", "53"]:
                test_calibration(cmd, choice)

            # 摄像头 61-63
            elif choice in ["61", "62", "63"]:
                test_camera(cmd, choice)

            # 轴控制 71-74
            elif choice in ["71", "72", "73", "74"]:
                test_axis(cmd, choice)

            # 灯光 81-83
            elif choice in ["81", "82", "83"]:
                test_light(cmd, choice)

            # 系统 91-95
            elif choice in ["91", "92", "93", "94", "95"]:
                test_system(cmd, choice)

            # X-Cam 101
            elif choice == "101":
                test_xcam(cmd, choice)

            # FTP 111-112
            elif choice in ["111", "112"]:
                test_ftp(choice)

            else:
                print("  未知命令，输入 h 查看帮助")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n中断")
    finally:
        client.disconnect()
        print("已断开连接")


if __name__ == "__main__":
    main()
