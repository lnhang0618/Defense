from entities.modes.attacker_modes.attacker_mode_base import Attacker_Mode_Base

class StraightDown(Attacker_Mode_Base):
    def update(self, radars, lasers, drones):
        # 更新无人机的方向
        for drone in drones:
            drone.direction = (0, -1)  # 保持向下飞行
            
        # 更新无人机位置
        for drone in drones:
            drone.move()  # 更新无人机位置