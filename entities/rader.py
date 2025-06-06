from math import sqrt

from utils.utils import cal_distance

class Radar:
    def __init__(self, config):
        self.config = config
        self.rader_id = self.config['id']
        self.position = self.config['position']
        self.radius = self.config['radius']
        self.max_tracks = self.config['max_tracks']
        
        self.tracked_drones = []  # 存储被雷达锁定的无人机
        self.in_range_drones = []
        
    def update(self, drones):
        
        # 每帧检测逻辑
        
        self.in_range_drones = [d for d in drones if cal_distance(self.position, d.position) <= self.radius]
    
    