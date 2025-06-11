from entities.modes.attacker_modes.attacker_mode_base import Attacker_Mode_Base
import random

class StraightDown(Attacker_Mode_Base):
    def update(self, radars, lasers, drones, infrastructures):
        # 更新无人机的方向:计算每个无人机的目标位置与当前位置的差向量
        for drone in drones:
            if not drone.succeed and not drone.destroyed:
                # 如果目标建筑物已经被摧毁，随机选择一个新的目标建筑物
                if drone.target_infrastructure and drone.target_infrastructure.destroyed:
                    # 随机选择一个新的目标建筑物
                    drone.target_infrastructure = None
                    available_infrastructures = [infra for infra in infrastructures if not infra.destroyed]
                    if available_infrastructures:
                        drone.target_infrastructure = random.choice(available_infrastructures)
                
                # 计算目标位置与当前位置的差向量
                target_position = drone.target_infrastructure.position if drone.target_infrastructure else (0, 0)
                direction_vector = (target_position[0] - drone.position[0],
                                    target_position[1] - drone.position[1])
                
                # 归一化方向向量
                norm = (direction_vector[0]**2 + direction_vector[1]**2)**0.5
                if norm > 0:
                    direction_vector = (direction_vector[0] / norm, direction_vector[1] / norm)
                
                # 更新无人机的方向
                drone.direction = direction_vector
            
        # 更新无人机位置
        for drone in drones:
            drone.move()  # 更新无人机位置