import numpy as np

class Drone:
    def __init__(self, world_config, drone_config):
        self.velocity = drone_config['velocity']
        
        self.drone_id = None # 需要在创建时设置
        self.position = None # 需要在创建时设置
        self.target_infrastructure = None
        self.health = 100
        self.detected_by_radar = False
        self.locked_by_radar = False
        self.succeed = False
        self.destroyed = False
        
        self.direction = None
        
    def move(self):
        if self.direction is None:
            raise ValueError("Direction must be set before updating the drone.")
        
        if self.succeed or self.destroyed:
            return # 如果无人机已经成功或被销毁，则不再更新位置
        
        # 正确更新位置
        new_x = self.position[0] + self.velocity * self.direction[0]
        new_y = self.position[1] + self.velocity * self.direction[1]
        self.position = (new_x, new_y)

        # 如果没有被锁定，恢复健康值
        # if not self.locked_by_radar:
        #     self.health = 100

        # 检查是否逃逸
        if np.linalg.norm(np.array(self.position) - np.array(self.target_infrastructure.position)) <= self.velocity:
            self.on_escape()
            
    def apply_damage(self, value):
        self.health -= value
        if self.health <= 20:
            self.on_destroy()
            
    def on_escape(self):
        print("Drone destroyed target infrastructure")
        self.succeed = True
        self.target_infrastructure.destroyed = True  # 目标基础设施被摧毁
        
    def on_destroy(self):
        print("Drone destroyed.")
        # 这里可以添加销毁后的逻辑，比如记录销毁时间等
        self.destroyed = True
        
        