"""
Bambu Lab 所有 MQTT 命令实现
共 56 个命令
"""

from typing import Optional, List, Dict, Any
from .client import BambuClient


class BambuCommands:
    """Bambu Lab 打印机命令集合"""

    def __init__(self, client: BambuClient):
        self.client = client

    def _seq(self) -> str:
        return self.client.get_sequence_id()

    # ========================================
    # 一、打印控制命令 (7个)
    # ========================================

    def stop(self) -> Dict:
        """停止打印"""
        return self.client.publish({
            "print": {
                "command": "stop",
                "param": "",
                "sequence_id": self._seq()
            }
        })

    def pause(self) -> Dict:
        """暂停打印"""
        return self.client.publish({
            "print": {
                "command": "pause",
                "param": "",
                "sequence_id": self._seq()
            }
        })

    def resume(self) -> Dict:
        """恢复打印"""
        return self.client.publish({
            "print": {
                "command": "resume",
                "param": "",
                "sequence_id": self._seq()
            }
        })

    def skip_objects(self, obj_list: List[int]) -> Dict:
        """跳过指定打印对象"""
        return self.client.publish({
            "print": {
                "command": "skip_objects",
                "obj_list": obj_list,
                "sequence_id": self._seq()
            }
        })

    def clean_print_error(self, subtask_id: str = "", print_error: int = 0) -> Dict:
        """清除打印错误"""
        return self.client.publish({
            "print": {
                "command": "clean_print_error",
                "subtask_id": subtask_id,
                "print_error": print_error,
                "sequence_id": self._seq()
            }
        })

    def gcode_line(self, gcode: str) -> Dict:
        """发送 G-code 命令"""
        return self.client.publish({
            "print": {
                "command": "gcode_line",
                "param": gcode,
                "sequence_id": self._seq()
            }
        })

    def gcode_file(self, file_path: str) -> Dict:
        """执行 G-code 文件"""
        return self.client.publish({
            "print": {
                "command": "gcode_file",
                "param": file_path,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 二、温度控制命令 (4个)
    # ========================================

    def set_bed_temp(self, temp: int) -> Dict:
        """设置热床温度"""
        return self.client.publish({
            "print": {
                "command": "set_bed_temp",
                "temp": temp,
                "sequence_id": self._seq()
            }
        })

    def set_nozzle_temp(self, temp: int, extruder_index: int = 0) -> Dict:
        """设置喷嘴温度"""
        return self.client.publish({
            "print": {
                "command": "set_nozzle_temp",
                "extruder_index": extruder_index,
                "target_temp": temp,
                "sequence_id": self._seq()
            }
        })

    def set_chamber_temp(self, temp: int) -> Dict:
        """设置腔室温度"""
        return self.client.publish({
            "print": {
                "command": "set_ctt",
                "ctt_val": temp,
                "sequence_id": self._seq()
            }
        })

    def refresh_nozzle(self) -> Dict:
        """刷新喷嘴状态"""
        return self.client.publish({
            "print": {
                "command": "refresh_nozzle",
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 三、风扇控制命令 (2个)
    # ========================================

    def set_fan(self, fan_index: int, speed: int) -> Dict:
        """
        设置风扇速度
        fan_index: 0=部件冷却风扇, 1=辅助风扇, 2=腔室风扇
        speed: 0-100
        """
        return self.client.publish({
            "print": {
                "command": "set_fan",
                "fan_index": fan_index,
                "speed": speed,
                "sequence_id": self._seq()
            }
        })

    def set_airduct(self, mode_id: int, submode: int = 0) -> Dict:
        """设置风道模式"""
        return self.client.publish({
            "print": {
                "command": "set_airduct",
                "modeId": mode_id,
                "submode": submode,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 四、AMS 自动换料系统命令 (6个)
    # ========================================

    def ams_change_filament(
        self,
        ams_id: int,
        slot_id: int,
        target: int = 0,
        curr_temp: int = 220,
        tar_temp: int = 220
    ) -> Dict:
        """更换 AMS 耗材"""
        return self.client.publish({
            "print": {
                "command": "ams_change_filament",
                "curr_temp": curr_temp,
                "tar_temp": tar_temp,
                "ams_id": ams_id,
                "target": target,
                "slot_id": slot_id,
                "sequence_id": self._seq()
            }
        })

    def ams_user_setting(
        self,
        ams_id: int = -1,
        startup_read: bool = True,
        tray_read: bool = True,
        calibrate_remain: bool = True
    ) -> Dict:
        """AMS 用户设置"""
        return self.client.publish({
            "print": {
                "command": "ams_user_setting",
                "ams_id": ams_id,
                "startup_read_option": startup_read,
                "tray_read_option": tray_read,
                "calibrate_remain_flag": calibrate_remain,
                "sequence_id": self._seq()
            }
        })

    def ams_filament_setting(
        self,
        ams_id: int,
        slot_id: int,
        tray_id: int,
        tray_type: str = "PLA",
        tray_color: str = "FFFFFFFF",
        nozzle_temp_min: int = 190,
        nozzle_temp_max: int = 230,
        setting_id: str = ""
    ) -> Dict:
        """AMS 耗材参数设置"""
        return self.client.publish({
            "print": {
                "command": "ams_filament_setting",
                "ams_id": ams_id,
                "slot_id": slot_id,
                "tray_id": tray_id,
                "tray_info_idx": 0,
                "setting_id": setting_id,
                "tray_color": tray_color,
                "nozzle_temp_min": nozzle_temp_min,
                "nozzle_temp_max": nozzle_temp_max,
                "tray_type": tray_type,
                "sequence_id": self._seq()
            }
        })

    def ams_get_rfid(self, ams_id: int, slot_id: int) -> Dict:
        """读取 AMS RFID 信息"""
        return self.client.publish({
            "print": {
                "command": "ams_get_rfid",
                "ams_id": ams_id,
                "slot_id": slot_id,
                "sequence_id": self._seq()
            }
        })

    def ams_control(self, action: str) -> Dict:
        """
        AMS 控制
        action: resume/reset/pause/done/abort
        """
        return self.client.publish({
            "print": {
                "command": "ams_control",
                "param": action,
                "sequence_id": self._seq()
            }
        })

    def ams_stop_dry(self) -> Dict:
        """停止 AMS 干燥"""
        return self.client.publish({
            "print": {
                "command": "auto_stop_ams_dry",
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 五、打印选项命令 (4个)
    # ========================================

    def set_print_speed(self, level: int) -> Dict:
        """
        设置打印速度
        level: 1=静音, 2=标准, 3=运动, 4=疯狂
        """
        return self.client.publish({
            "print": {
                "command": "print_speed",
                "param": str(level),
                "sequence_id": self._seq()
            }
        })

    def set_print_option(
        self,
        auto_recovery: bool = True,
        nozzle_blob_detect: bool = True,
        sound_enable: bool = True,
        filament_tangle_detect: bool = True,
        auto_switch_filament: bool = True,
        air_print_detect: bool = True
    ) -> Dict:
        """设置打印选项"""
        return self.client.publish({
            "print": {
                "command": "print_option",
                "option": 1,
                "auto_recovery": auto_recovery,
                "nozzle_blob_detect": nozzle_blob_detect,
                "sound_enable": sound_enable,
                "filament_tangle_detect": filament_tangle_detect,
                "auto_switch_filament": auto_switch_filament,
                "air_print_detect": air_print_detect,
                "sequence_id": self._seq()
            }
        })

    def set_extrusion_length(self, length: float, extruder_index: int = 0) -> Dict:
        """控制挤出长度"""
        return self.client.publish({
            "print": {
                "command": "set_extrusion_length",
                "extruder_index": extruder_index,
                "length": length,
                "sequence_id": self._seq()
            }
        })

    def set_anti_heating_mode(self, enable: bool) -> Dict:
        """设置防止持续加热模式"""
        return self.client.publish({
            "print": {
                "command": "set_against_continued_heating_mode",
                "enable": enable,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 六、校准命令 (9个)
    # ========================================

    def calibration(self, option: int = 127) -> Dict:
        """
        综合校准
        option 位掩码:
          1 = 振动校准
          2 = 床平整
          4 = X-cam
          8 = 电机噪音
          16 = 喷嘴
          32 = 床
          64 = 夹紧位置
        """
        return self.client.publish({
            "print": {
                "command": "calibration",
                "option": option,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali(
        self,
        tray_id: int,
        nozzle_temp: int = 220,
        bed_temp: int = 60,
        max_volumetric_speed: float = 10.0
    ) -> Dict:
        """挤出量校准"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali",
                "tray_id": tray_id,
                "nozzle_temp": nozzle_temp,
                "bed_temp": bed_temp,
                "max_volumetric_speed": max_volumetric_speed,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali_set(
        self,
        tray_id: int,
        k_value: float,
        n_coef: float = 1.4,
        nozzle_temp: int = 220,
        bed_temp: int = 60,
        max_volumetric_speed: float = 10.0
    ) -> Dict:
        """保存挤出量校准参数"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali_set",
                "tray_id": tray_id,
                "k_value": k_value,
                "n_coef": n_coef,
                "bed_temp": bed_temp,
                "nozzle_temp": nozzle_temp,
                "max_volumetric_speed": max_volumetric_speed,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali_get(self, filament_id: str, nozzle_diameter: str = "0.4") -> Dict:
        """获取挤出量校准数据"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali_get",
                "filament_id": filament_id,
                "nozzle_diameter": nozzle_diameter,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali_del(
        self,
        extruder_id: int,
        nozzle_id: str,
        filament_id: str,
        cali_idx: int,
        nozzle_diameter: str = "0.4"
    ) -> Dict:
        """删除挤出量校准数据"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali_del",
                "extruder_id": extruder_id,
                "nozzle_id": nozzle_id,
                "filament_id": filament_id,
                "cali_idx": cali_idx,
                "nozzle_diameter": nozzle_diameter,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali_sel(
        self,
        tray_id: int,
        ams_id: int,
        slot_id: int,
        cali_idx: int,
        filament_id: str,
        nozzle_diameter: str = "0.4"
    ) -> Dict:
        """选择挤出量校准配置"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali_sel",
                "tray_id": tray_id,
                "ams_id": ams_id,
                "slot_id": slot_id,
                "cali_idx": cali_idx,
                "filament_id": filament_id,
                "nozzle_diameter": nozzle_diameter,
                "sequence_id": self._seq()
            }
        })

    def extrusion_cali_get_result(self, nozzle_diameter: str = "0.4") -> Dict:
        """获取挤出量校准结果"""
        return self.client.publish({
            "print": {
                "command": "extrusion_cali_get_result",
                "nozzle_diameter": nozzle_diameter,
                "sequence_id": self._seq()
            }
        })

    def flowrate_cali(
        self,
        tray_id: int,
        filament_id: str,
        setting_id: str,
        nozzle_temp: int = 220,
        bed_temp: int = 60,
        max_volumetric_speed: float = 10.0,
        nozzle_diameter: str = "0.4"
    ) -> Dict:
        """流量比校准"""
        return self.client.publish({
            "print": {
                "command": "flowrate_cali",
                "tray_id": tray_id,
                "nozzle_diameter": nozzle_diameter,
                "filaments": [{
                    "tray_id": tray_id,
                    "bed_temp": bed_temp,
                    "filament_id": filament_id,
                    "setting_id": setting_id,
                    "nozzle_temp": nozzle_temp,
                    "def_flow_ratio": "1.0",
                    "max_volumetric_speed": str(max_volumetric_speed),
                    "extruder_id": 0,
                    "ams_id": 0,
                    "slot_id": 0
                }],
                "sequence_id": self._seq()
            }
        })

    def flowrate_get_result(self, nozzle_diameter: str = "0.4") -> Dict:
        """获取流量比校准结果"""
        return self.client.publish({
            "print": {
                "command": "flowrate_get_result",
                "nozzle_diameter": nozzle_diameter,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 七、摄像头控制命令 (3个)
    # ========================================

    def camera_record(self, enable: bool) -> Dict:
        """启用/禁用摄像头录制"""
        return self.client.publish({
            "camera": {
                "command": "ipcam_record_set",
                "control": "enable" if enable else "disable",
                "sequence_id": self._seq()
            }
        })

    def camera_timelapse(self, enable: bool) -> Dict:
        """启用/禁用延时摄影"""
        return self.client.publish({
            "camera": {
                "command": "ipcam_timelapse",
                "control": "enable" if enable else "disable",
                "sequence_id": self._seq()
            }
        })

    def camera_resolution(self, resolution: str = "1080p") -> Dict:
        """设置摄像头分辨率"""
        return self.client.publish({
            "camera": {
                "command": "ipcam_resolution_set",
                "resolution": resolution,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 八、X-Cam AI 检测命令 (1个)
    # ========================================

    def xcam_control(
        self,
        module: str,
        enable: bool,
        print_halt: bool = False,
        sensitivity: str = "medium"
    ) -> Dict:
        """
        X-Cam 控制
        module: printing_monitor / first_layer_inspector / buildplate_marker_detector
        sensitivity: low / medium / high
        """
        return self.client.publish({
            "xcam": {
                "command": "xcam_control_set",
                "module_name": module,
                "control": enable,
                "enable": enable,
                "print_halt": print_halt,
                "halt_print_sensitivity": sensitivity,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 九、轴控制命令 (3个)
    # ========================================

    def home(self) -> Dict:
        """回原点 (G28)"""
        return self.gcode_line("G28")

    def back_to_center(self) -> Dict:
        """回到中心位置"""
        return self.client.publish({
            "print": {
                "command": "back_to_center",
                "sequence_id": self._seq()
            }
        })

    def move_axis(self, axis: str, direction: int, mode: int = 0) -> Dict:
        """
        移动轴
        axis: X/Y/Z/E
        direction: 1=正向, -1=反向
        mode: 0=小步, 1=大步
        """
        return self.client.publish({
            "print": {
                "command": "xyz_ctrl",
                "axis": axis.upper(),
                "dir": direction,
                "mode": mode,
                "sequence_id": self._seq()
            }
        })

    def select_extruder(self, index: int) -> Dict:
        """选择挤出机"""
        return self.client.publish({
            "print": {
                "command": "select_extruder",
                "extruder_index": index,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 十、灯光控制命令 (1个)
    # ========================================

    def light(
        self,
        mode: str,
        node: str = "chamber_light",
        on_time: int = 500,
        off_time: int = 500,
        loops: int = 1,
        interval: int = 1000
    ) -> Dict:
        """
        灯光控制
        mode: on/off/flashing
        node: chamber_light / chamber_light2
        """
        return self.client.publish({
            "system": {
                "command": "ledctrl",
                "led_node": node,
                "led_mode": mode,
                "led_on_time": on_time,
                "led_off_time": off_time,
                "loop_times": loops,
                "interval_time": interval,
                "sequence_id": self._seq()
            }
        })

    def light_on(self) -> Dict:
        """开灯"""
        return self.light("on")

    def light_off(self) -> Dict:
        """关灯"""
        return self.light("off")

    def light_flash(self, loops: int = 3) -> Dict:
        """闪烁"""
        return self.light("flashing", loops=loops)

    # ========================================
    # 十一、喷嘴架控制命令 (4个)
    # ========================================

    def nozzle_holder_ctrl(self, action: int) -> Dict:
        """
        喷嘴架控制
        action: 0=回家, 1=A顶部, 2=B顶部
        """
        return self.client.publish({
            "print": {
                "command": "nozzle_holder_ctrl",
                "action": action,
                "sequence_id": self._seq()
            }
        })

    def nozzle_info_confirm(self, nozzle_id: int) -> Dict:
        """确认喷嘴信息"""
        return self.client.publish({
            "print": {
                "command": "nozzle_info_confirm",
                "id": nozzle_id,
                "sequence_id": self._seq()
            }
        })

    def nozzle_refresh(self, nozzle_id: int) -> Dict:
        """刷新喷嘴架信息"""
        return self.client.publish({
            "print": {
                "command": "holder_nozzle_refresh",
                "id": nozzle_id,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 十二、系统命令 (5个)
    # ========================================

    def get_version(self) -> Dict:
        """获取固件版本"""
        return self.client.publish({
            "info": {
                "command": "get_version",
                "sequence_id": self._seq()
            }
        })

    def get_access_code(self) -> Dict:
        """获取访问码"""
        return self.client.publish({
            "system": {
                "command": "get_access_code",
                "sequence_id": self._seq()
            }
        })

    def push_all(self) -> Dict:
        """请求所有状态"""
        return self.client.publish({
            "pushing": {
                "command": "pushall",
                "version": 1,
                "push_target": 1,
                "sequence_id": self._seq()
            }
        })

    def set_door_detection(self, config: int) -> Dict:
        """
        设置门状态检测
        config: 0=禁用, 1=警告, 2=暂停打印
        """
        return self.client.publish({
            "system": {
                "command": "set_door_stat",
                "config": config,
                "sequence_id": self._seq()
            }
        })

    def set_print_cache(self, enable: bool) -> Dict:
        """设置打印缓存"""
        return self.client.publish({
            "system": {
                "command": "print_cache_set",
                "config": enable,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 十三、固件升级命令 (3个)
    # ========================================

    def upgrade_confirm(self, src_id: int = 1) -> Dict:
        """确认固件升级"""
        return self.client.publish({
            "upgrade": {
                "command": "upgrade_confirm",
                "src_id": src_id,
                "sequence_id": self._seq()
            }
        })

    def upgrade_start(self, url: str, module: str, version: str, src_id: int = 1) -> Dict:
        """启动固件升级"""
        return self.client.publish({
            "upgrade": {
                "command": "start",
                "url": url,
                "module": module,
                "version": version,
                "src_id": src_id,
                "sequence_id": self._seq()
            }
        })

    def consistency_confirm(self, src_id: int = 1) -> Dict:
        """确认一致性检查"""
        return self.client.publish({
            "upgrade": {
                "command": "consistency_confirm",
                "src_id": src_id,
                "sequence_id": self._seq()
            }
        })

    # ========================================
    # 十四、错误处理命令 (3个)
    # ========================================

    def buzzer_off(self) -> Dict:
        """关闭蜂鸣器"""
        return self.client.publish({
            "print": {
                "command": "buzzer_ctrl",
                "mode": 0,
                "sequence_id": self._seq()
            }
        })

    def ignore_error(self, error: str, job_id: str = "") -> Dict:
        """忽略错误"""
        return self.client.publish({
            "print": {
                "command": "ignore",
                "err": error,
                "param": "reserve",
                "job_id": job_id,
                "sequence_id": self._seq()
            }
        })

    def close_dialog(self, name: str = "print_error", error: str = "00000000") -> Dict:
        """关闭 UI 对话框"""
        return self.client.publish({
            "system": {
                "command": "uiop",
                "name": name,
                "action": "close",
                "source": 1,
                "type": "dialog",
                "err": error,
                "sequence_id": self._seq()
            }
        })
