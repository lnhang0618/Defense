from entities.drone import Drone
from entities.laser import Laser
from entities.radar import Radar
from entities.infrastructure import Infrastructure
from utils.utils import cal_distance
from utils.vis import Visualizer
from managers.mode_manager import Mode_Manager


import random
import matplotlib.pyplot as plt
import yaml
import math


class GameManager:
    def __init__(self, config_path):
        
        # load yaml config
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.world_config = config['world']
        self.visualizer = Visualizer(self.world_config)
        self.visualizer.init_plot()
        
        self.attacker_mode_manager = Mode_Manager(robot_type="Attacker")
        self.defensor_mode_manager = Mode_Manager(robot_type="Defensor")

        # 初始化组件
        self.radars = []
        for key in config['radar']:
            self.radars.append(Radar(self.world_config, config['radar'][key]))

        self.lasers = []
        for key in config['laser']:
            self.lasers.append(Laser(config['laser'][key]))
            
        self.infrastructures = []
        for key in config['infrastructure']:
            self.infrastructures.append(Infrastructure(config['infrastructure'][key]))

        # 初始无无人机
        self.drones = []
        self.drone_config = config['drone']

        # 控制无人机生成参数
        self.spawn_interval = self.drone_config.get('spawn_interval', 5)  # 每隔多少步生成一次
        self.spawn_num = self.drone_config.get('spawn_num', 1)  # 每次生成的数量
        self.spawn_probability = self.drone_config.get('spawn_probability', 0.3)  # 每次生成的概率
        self.step_count = 0
        
        # 可选：用于记录唯一 drone_id
        self.next_drone_id = 1
        
        self.random_seed = config.get('random_seed', 42)
        random.seed(self.random_seed)
    
    def spawn_drone(self):
        for _ in range(self.spawn_num):
            if random.random() < self.spawn_probability:
                # 从 world_config 中获取圆心和半径
                map_center = self.world_config['map_center']
                map_radius = self.world_config['map_radius']
                
                # 获取 attack_angle 配置，如果存在则限制生成角度范围
                attack_angle = self.drone_config.get('attack_angle', None)
                
                if attack_angle is not None:
                    start_angle, end_angle = attack_angle
                    # 转为弧度
                    start_angle, end_angle = math.radians(start_angle), math.radians(end_angle)
                    theta = random.uniform(start_angle, end_angle)
                else:
                    theta = random.uniform(0, 2 * math.pi)
                
                # 计算圆周上的点
                cx, cy = map_center
                x = cx + map_radius * math.cos(theta)
                y = cy + map_radius * math.sin(theta)
                
                # 创建无人机
                drone = Drone(self.world_config, self.drone_config)
                drone.drone_id = self.next_drone_id
                self.next_drone_id += 1
                
                # 设置位置
                drone.position = (x, y)
                
                # 设置初始目标,随机选择一个基础设施作为目标
                drone.target_infrastructure = random.choice(self.infrastructures)
                
                self.drones.append(drone)
        
    def update_attacker(self):
        # 更新攻击者模式
        active_mode = self.attacker_mode_manager.update_and_get_active_modes(self.radars, self.lasers, self.drones, self.infrastructures)
        if active_mode:
            active_mode.update(self.radars, self.lasers, self.drones, self.infrastructures)
    
    def update_defensor(self):
        # 更新防御者模式
        active_mode = self.defensor_mode_manager.update_and_get_active_modes(self.radars, self.lasers, self.drones, self.infrastructures)
        if active_mode:
            active_mode.update(self.radars, self.lasers, self.drones, self.infrastructures)

    def check_end_condition(self):        
        # 检查是否有基础设施存活
        if all(infra.destroyed for infra in self.infrastructures):
            print("所有基础设施已被摧毁，游戏结束。")
            return True
        return False

    def step(self):
        self.step_count += 1
        # 根据间隔生成无人机
        if self.step_count % self.spawn_interval == 0:
            self.spawn_drone()
        # 更新攻击者和防御者模式
        self.update_attacker()
        self.update_defensor()
    
    def start_simulation(self, max_steps=300, output_file="simulation.mp4"):
        for step in range(max_steps):
            self.step()
            self.visualizer.draw(self.drones, self.radars, self.lasers, self.infrastructures)
            self.visualizer.record_frame()
            
            if self.check_end_condition():
                break
        # 保存视频
        self.visualizer.save_video("simulation.mp4")