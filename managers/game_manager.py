from entities.drone import Drone
from entities.laser import Laser
from entities.radar import Radar
from utils.utils import cal_distance
from utils.vis import Visualizer
import random
import matplotlib.pyplot as plt
import yaml


class GameManager:
    def __init__(self, config_path):
        
        # load yaml config
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.world_config = config['world']
        self.visualizer = Visualizer(self.world_config)

        # 初始化组件
        self.radars = []
        for key in config['radar']:
            self.radars.append(Radar(config['radar'][key]))

        self.lasers = []
        for key in config['laser']:
            self.lasers.append(Laser(config['laser'][key]))

        # 初始无无人机
        self.drones = []
        self.drone_config = config['drone']

        # 控制无人机生成参数
        self.spawn_interval = config.get('spawn_interval', 5)  # 每隔多少步生成一次
        self.spawn_probability = config.get('spawn_probability', 0.3)  # 每次生成的概率
        self.step_count = 0
        
        # 可选：用于记录唯一 drone_id
        self.next_drone_id = 1
        
        self.random_seed = config.get('random_seed', 42)
        random.seed(self.random_seed)
    
    def spawn_drone(self):

        if random.random() < self.spawn_probability:
            x_min, x_max = self.world_config['x_bounds']
            y_top = self.world_config['y_bounds'][1] - 10  # 假设从上边界生成

            drone = Drone(self.world_config, self.drone_config)
            drone.drone_id = self.next_drone_id
            self.next_drone_id += 1

            drone.position = (random.uniform(x_min, x_max), y_top)
            drone.direction = (0, -1)  # 默认向下飞行
            self.drones.append(drone)
            
    def update_drones(self):
        for drone in self.drones:
            drone.move()

    def step(self):
        self.step_count += 1
        # 根据间隔生成无人机
        if self.step_count % self.spawn_interval == 0:
            self.spawn_drone()
        # 更新无人机
        self.update_drones()

    def start_simulation(self, max_steps=1000):
        plt.ion()  # 启用交互模式
        for step in range(max_steps):
            try:
                self.step()
                self.visualizer.draw(self.drones, self.radars, self.lasers)
                plt.draw()
                plt.pause(0.1)
                if not plt.fignum_exists(self.visualizer.fig.number):
                    print("Simulation window closed.")
                    break
            except Exception as e:
                print(f"Error during simulation: {e}")
                break
        plt.close(self.visualizer.fig)
        print("Simulation ended.")