from math import sqrt

from utils.utils import cal_distance

class Radar:
    def __init__(self, world_config, radar_config):
        self.world_config = world_config
        self.radar_config = radar_config
        self.radar_id =self.radar_config['id']
        self.position =self.radar_config['position']
        self.radius =self.radar_config['radius']
        self.max_tracks =self.radar_config['max_tracks']
        
        self.tracked_drones = []  # 存储被雷达锁定的无人机
        self.cooperate_lasers = []  # 存储与雷达协作的激光炮
        self.detected_drones = []
        
    def detect_drones(self, drones):
        
        # 每帧检测逻辑
        
        # 在雷达范围内的无人机，并且无人机的状态不是逃逸或销毁
        self.detected_drones = [d for d in drones if cal_distance(self.position, d.position) <= self.radius and not (d.succeed or d.destroyed)]
        
        for drone in self.detected_drones:
            drone.detected_by_radar = True
            
        # 计算剩余窗口期（无人机还有多久会逃出雷达范围）
        self.drone_window_periods_dict = self.cal_window_period()
        
    def lock_on_drone(self, drone):
        """将雷达锁定到指定的无人机"""
        
        self.tracked_drones.append(drone)
        
    def cal_window_period(self):
        ''' 
        通过几何关系简单估计
        
        T_u = y_{drone} - (y_{radar} - sqrt(r^2 - (x_{drone} - x_{radar})^2)) / v_{drone}
        '''
        
        drone_window_periods_dict = {}
        
        for drone in self.detected_drones:
            x_drone, y_drone = drone.position
            x_radar, y_radar = self.position
            
            survival_time = (y_drone - (y_radar - sqrt(self.radius**2 - (x_drone - x_radar)**2))) / drone.velocity
            
            drone_window_periods_dict[drone.drone_id] = survival_time
        
        return drone_window_periods_dict
            
        
        
    
    