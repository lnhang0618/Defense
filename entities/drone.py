class Drone:
    def __init__(self, world_config, drone_config):
        self.speed = drone_config['speed']
        self.x_bounds = world_config['x_bounds']
        self.y_bounds = world_config['y_bounds']
        
        self.direction = (0, -1) # demo中写定为向下，未来可以根据需要调整
        
        self.drone_id = None # 需要在创建时设置
        self.position = None # 需要在创建时设置
        self.health = 100
        self.locked_raders = []
        self.escaped = False
        self.destroyed = False
        
    def update(self):
        self.position = (self.position + self.speed * self.direction)
        
        if len(self.locked_raders) == 0:
            self.health = 100  # 如果没有被锁定，恢复健康值
        
        if self.position[1] < self.y_bounds[0]:
            self.on_escape()
            
    def apply_damage(self, value):
        self.health -= value
        if self.health <= 0:
            self.on_destroy()
            
    def on_escape(self):
        print("Drone escaped the area.")
        # 这里可以添加逃离后的逻辑，比如记录逃离时间等
        self.escaped = True
        
    def on_destroy(self):
        print("Drone destroyed.")
        # 这里可以添加销毁后的逻辑，比如记录销毁时间等
        self.destroyed = True
        
        