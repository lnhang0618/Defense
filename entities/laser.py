from math import sqrt

from utils.utils import cal_distance

class Laser:
    def __init__(self, config):
        self.config = config
        self.laser_id = self.config['id']
        self.position = self.config['position']
        # self.radius = self.config['radius']
        
        self.target_drone = None
        self.coorperate_radar = None
        self.charge_rate = 10.0
        
    def attack_drone(self):
        
        self.drone_survival_time = {}
        
        if self.target_drone:
            distance = cal_distance(self.position, self.target_drone.position)
            effective_rate = self.get_effective_rate()
            self.target_drone.apply_damage(effective_rate)
            
            self.drone_survival_time[self.target_drone.drone_id] = (self.target_drone.health-20) / effective_rate
            
    def get_effective_rate(self, drone=None):
        
        if not drone:
            drone = self.target_drone
        
        if not drone:
            return 0
        else:
            distance = cal_distance(self.position, drone.position)
            return self.charge_rate / (distance/100 + 1)
            
    
            