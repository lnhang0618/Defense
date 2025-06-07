from math import sqrt

from utils.utils import cal_distance

class Laser:
    def __init__(self, config):
        self.config = config
        self.laser_id = self.config['id']
        self.position = self.config['position']
        # self.radius = self.config['radius']
        
        self.target_drone = None
        self.charge_rate = 10
        
    def attack_drone(self):
        
        if self.target_drone:
            distance = cal_distance(self.position, self.target_drone.position)
            effective_rate = self.charge_rate / (distance/100 + 0.01) # 避免除以0
            self.target_drone.apply_damage(effective_rate)
            