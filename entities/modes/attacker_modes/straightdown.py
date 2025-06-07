from entities.modes.attacker_modes.attacker_mode_base import Attacker_Mode_Base

class StraightDown(Attacker_Mode_Base):
    def update_drones(self, drones):
        for drone in drones:
            drone.direction = (0, -1)  # 保持向下飞行