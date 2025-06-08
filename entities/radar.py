from math import sqrt

from utils.utils import cal_distance

class Radar:
    def __init__(self, config):
        self.config = config
        self.radar_id = self.config['id']
        self.position = self.config['position']
        self.radius = self.config['radius']
        self.max_tracks = self.config['max_tracks']
        
        self.tracked_drones = []  # 存储被雷达锁定的无人机
        self.detected_drones = []
        
    def detect_drones(self, drones):
        
        # 每帧检测逻辑
        
        # 在雷达范围内的无人机，并且无人机的状态不是逃逸或销毁
        self.detected_drones = [d for d in drones if cal_distance(self.position, d.position) <= self.radius and not (d.escaped or d.destroyed)]
        
        for drone in self.detected_drones:
            drone.detected_by_radar = True
        
    def lock_on_drone(self, drone):
        """将雷达锁定到指定的无人机"""
        
        self.tracked_drones.append(drone)
        
        
    
    