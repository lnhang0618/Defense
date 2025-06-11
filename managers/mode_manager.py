from entities.modes.attacker_modes.straightdown import StraightDown
from entities.modes.defensor_modes.closetfirst import ClosestFirst


class Mode_Manager:
    def __init__(self, robot_type):
        self.modes = {}
        self.active_mode = None
        self.robot_type = robot_type
        
        self._add_modes()
        
    def _add_modes(self):
        if self.robot_type == "Defensor":
            self.modes["ClosestFirst"] = ClosestFirst
            
        elif self.robot_type == "Attacker":
            self.modes["StraightDown"] = StraightDown
        
    def set_mode(self, mode_name):
        """设置当前活动模式"""
        if mode_name in self.modes:
            self.active_mode = self.modes[mode_name]()
        else:
            raise ValueError(f"Mode {mode_name} not found.")
        
    def update_and_get_active_modes(self, radars, lasers, drones, infrastructures):
        # 在此设置规则，更新活动模式并返回当前活动模式,目前版本写死
        
        if self.robot_type == "Defensor":
            self.set_mode("ClosestFirst")
        elif self.robot_type == "Attacker":
            self.set_mode("StraightDown")

        else:
            raise ValueError(f"Unknown robot type: {self.robot_type}")
        
        """获取当前活动模式"""
        return self.active_mode