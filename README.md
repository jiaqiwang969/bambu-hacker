# Bambu Lab H2S 完整控制库

通过逆向工程实现对拓竹 H2S 3D打印机的完全本地控制，脱离官方 App 限制。

## 实现原理

### 1. 协议分析

通过分析 [BambuStudio 开源代码](https://github.com/bambulab/BambuStudio)，发现打印机使用以下通信方式：

| 项目 | 值 |
|------|-----|
| 协议 | MQTT over TLS |
| 端口 | 8883 |
| 用户名 | `bblp` (固定) |
| 密码 | 打印机 Access Code |
| 消息格式 | JSON |

### 2. MQTT Topic 结构

```
device/{序列号}/request   # 发送命令
device/{序列号}/report    # 接收状态
```

### 3. 命令格式

所有命令使用 JSON 格式，包含 `sequence_id` 用于追踪：

```json
{
  "print": {
    "command": "gcode_line",
    "param": "G28",
    "sequence_id": "1"
  }
}
```

### 4. 关键源码位置

从 BambuStudio 源码中提取的关键文件：

| 功能 | 文件路径 |
|------|----------|
| 网络定义 | `src/slic3r/Utils/bambu_networking.hpp` |
| 设备管理 | `src/slic3r/GUI/DeviceManager.cpp` |
| 灯光控制 | `src/slic3r/GUI/DeviceCore/DevLampCtrl.cpp` |
| 轴控制 | `src/slic3r/GUI/DeviceCore/DevAxisCtrl.cpp` |

## 已实现功能 (56 个命令)

### 打印控制 (7个)
- `stop` - 停止打印
- `pause` - 暂停打印
- `resume` - 恢复打印
- `skip_objects` - 跳过指定对象
- `clean_print_error` - 清除打印错误
- `gcode_line` - 发送 G-code
- `gcode_file` - 执行 G-code 文件

### 温度控制 (4个)
- `set_bed_temp` - 设置热床温度
- `set_nozzle_temp` - 设置喷嘴温度
- `set_ctt` - 设置腔室温度
- `refresh_nozzle` - 刷新喷嘴状态

### 风扇控制 (2个)
- `set_fan` - 设置风扇速度 (0=部件冷却, 1=辅助, 2=腔室)
- `set_airduct` - 设置风道模式

### AMS 自动换料系统 (6个)
- `ams_change_filament` - 更换耗材
- `ams_user_setting` - AMS 用户设置
- `ams_filament_setting` - 耗材参数设置
- `ams_get_rfid` - 读取 RFID 信息
- `ams_control` - AMS 控制 (resume/reset/pause/done/abort)
- `auto_stop_ams_dry` - 停止 AMS 干燥

### 打印选项 (4个)
- `print_speed` - 设置打印速度 (1=静音, 2=标准, 3=运动, 4=疯狂)
- `print_option` - 打印选项 (自动恢复、声音、缠绕检测等)
- `set_extrusion_length` - 控制挤出长度
- `set_against_continued_heating_mode` - 防止持续加热模式

### 校准功能 (9个)
- `calibration` - 综合校准 (振动、床平整、X-cam、电机噪音等)
- `extrusion_cali` - 挤出量校准
- `extrusion_cali_set` - 保存校准参数
- `extrusion_cali_get` - 获取校准数据
- `extrusion_cali_del` - 删除校准数据
- `extrusion_cali_sel` - 选择校准配置
- `extrusion_cali_get_result` - 获取校准结果
- `flowrate_cali` - 流量比校准
- `flowrate_get_result` - 获取流量校准结果

### 摄像头控制 (3个)
- `ipcam_record_set` - 启用/禁用录制
- `ipcam_timelapse` - 启用/禁用延时摄影
- `ipcam_resolution_set` - 设置分辨率

### X-Cam AI 检测 (1个)
- `xcam_control_set` - 控制 AI 检测模块

### 轴控制 (4个)
- `home` (G28) - 回原点
- `back_to_center` - 回到中心位置
- `xyz_ctrl` - XYZ/E 轴移动控制
- `select_extruder` - 选择挤出机

### 灯光控制 (4个)
- `ledctrl` - 灯光控制 (on/off/flashing)
- `light_on` - 开灯
- `light_off` - 关灯
- `light_flash` - 闪烁

### 系统命令 (5个)
- `get_version` - 获取固件版本
- `get_access_code` - 获取访问码
- `pushall` - 请求所有状态
- `set_door_stat` - 门状态检测设置
- `print_cache_set` - 打印缓存设置

### 固件升级 (3个)
- `upgrade_confirm` - 确认升级
- `upgrade_start` - 启动升级
- `consistency_confirm` - 一致性确认

### 错误处理 (3个)
- `buzzer_ctrl` - 蜂鸣器控制
- `ignore` - 忽略错误
- `uiop` - UI 操作 (关闭对话框)

### FTP 文件操作 (5个)
- `connect` - 连接 FTP (端口 990, FTPS)
- `upload_file` - 上传打印文件
- `download_file` - 下载文件
- `list_files` - 列出文件
- `delete_file` - 删除文件

## 无法实现的功能

| 功能 | 原因 |
|------|------|
| 修改固件 | 固件签名验证 |
| 获取 root 权限 | 需要硬件逆向 (UART/JTAG) |
| 解锁隐藏功能 | 固件层面限制 |
| 修改温度/速度上限 | 硬编码在固件中 |
| 禁用安全检查 | 固件保护 |

## 项目结构

```
161-bambu-hacker/
├── bambu_h2s/              # Python 控制库
│   ├── __init__.py
│   ├── client.py           # MQTT 客户端封装
│   ├── commands.py         # 56 个命令实现
│   └── ftp.py              # FTP 文件上传
├── bambu_control.py        # 简单交互控制脚本
├── test_all.py             # 完整功能测试程序
├── test_quick.py           # 快速安全测试
├── venv/                   # Python 虚拟环境
└── README.md
```

## 快速开始

### 1. 获取打印机信息

在打印机屏幕上查看：
- **IP 地址**: 设置 → 网络 → IP
- **Access Code**: 设置 → 网络 → 访问码
- **序列号**: 设置 → 设备 → 序列号 (可自动获取)

### 2. 运行测试

```bash
cd ~/161-bambu-hacker
source venv/bin/activate

# 快速测试 (安全，不影响打印)
python3 test_quick.py

# 完整交互测试
python3 test_all.py
```

### 3. 在代码中使用

```python
from bambu_h2s import BambuClient, BambuCommands

# 连接打印机
client = BambuClient("192.168.31.58", "your_access_code")
client.connect()

# 创建命令对象
cmd = BambuCommands(client)

# 控制打印机
cmd.light_on()                    # 开灯
cmd.set_bed_temp(60)              # 热床 60°C
cmd.set_nozzle_temp(200)          # 喷嘴 200°C
cmd.gcode_line("G28")             # 回原点
cmd.set_print_speed(2)            # 标准速度
cmd.push_all()                    # 获取状态

# 读取状态
print(client.state)               # {'gcode_state': 'IDLE', 'nozzle_temper': 200, ...}

# 断开连接
client.disconnect()
```

### 4. FTP 上传打印文件

```python
from bambu_h2s import BambuFTP

with BambuFTP("192.168.31.58", "your_access_code") as ftp:
    # 上传文件到打印机
    ftp.upload_file("model.3mf")

    # 列出文件
    files = ftp.list_files("/cache/")
    print(files)
```

## 配置说明

修改 `bambu_control.py` 或测试脚本中的配置：

```python
PRINTER_IP = "192.168.31.58"    # 你的打印机 IP
ACCESS_CODE = "xxxxxxxx"         # 你的 Access Code
```

## 依赖

- Python 3.8+
- paho-mqtt

已包含在 venv 中，无需额外安装。

## 参考资料

- [BambuStudio 源码](https://github.com/bambulab/BambuStudio)
- [Home Assistant Bambu Lab 集成](https://github.com/greghesp/ha-bambulab)

## 免责声明

本项目仅供学习和研究目的。使用本工具控制打印机时请注意安全，作者不对任何损失负责。

## License

MIT
