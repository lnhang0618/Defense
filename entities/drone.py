class Drone:
    def __init__(self, world_config, drone_config):
        self.speed = drone_config['speed']
        self.x_bounds = world_config['x_bounds']
        self.y_bounds = world_config['y_bounds']
        
        self.drone_id = None # 需要在创建时设置
        self.position = None # 需要在创建时设置
        self.health = 100
        self.locked_raders = []
        self.escaped = False
        self.destroyed = False
        
        self.direction = None
        
    def move(self):
        if self.direction is None:
            raise ValueError("Direction must be set before updating the drone.")
        
        if self.escaped or self.destroyed:
            return # 如果无人机已经逃逸或被销毁，则不再更新位置
        
        # 正确更新位置
        new_x = self.position[0] + self.speed * self.direction[0]
        new_y = self.position[1] + self.speed * self.direction[1]
        self.position = (new_x, new_y)

        # 如果没有被锁定，恢复健康值
        if len(self.locked_raders) == 0:
            self.health = 100

        # 检查是否逃逸
        if self.position[1] < self.y_bounds[0] + 5: # 假设逃逸条件是 y 坐标小于下边界 + 5
            self.on_escape()
            
    def apply_damage(self, value):
        self.health -= value
        if self.health <= 20:
            self.on_destroy()
            
    def on_escape(self):
        print("Drone escaped the area.")
        # 这里可以添加逃离后的逻辑，比如记录逃离时间等
        self.escaped = True
        
    def on_destroy(self):
        print("Drone destroyed.")
        # 这里可以添加销毁后的逻辑，比如记录销毁时间等
        self.destroyed = True
        
        