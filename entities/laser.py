from math import sqrt

from utils.utils import cal_distance

class Laser:
    def __init__(self, config):
        self.config = config
        self.laser_id = self.config['id']
        self.position = self.config['position']
        self.radius = self.config['radius']
        
        self.target_drone = None
        self.charge_rate = 1.0
        
    def update(self):
        if self.target_drone:
            distance = cal_distance(self.position, self.target_drone.position)
            effective_rate = self.charge_rate / (distance/100 + 1)
            self.target_drone.apply_damage(effective_rate)
            