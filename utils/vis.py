import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import matplotlib.lines as mlines

class Visualizer:
    def __init__(self, world_config):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.set_xlim(world_config['x_bounds'])
        self.ax.set_ylim(world_config['y_bounds'])
        self.ax.set_aspect('equal')
        self.ax.set_title("Drone Simulation")
        self.ax.grid(True)

    def draw(self, drones, radars, lasers):
        # 保存清除前的坐标轴范围
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # 清除当前绘图内容
        self.ax.clear()
        
        # 恢复坐标轴范围
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_title("Drone Simulation")

        # 绘制雷达
        for radar in radars:
            self.ax.scatter(radar.position[0], radar.position[1], color='blue', marker='^', s=100)
            
            # 绘制雷达的扫描范围
            outer_circle = Circle(radar.position, radar.radius, color='blue', fill=False, linestyle='--', linewidth=1.5)
            self.ax.add_patch(outer_circle)
            
            # 绘制雷达跟踪的无人机
            for drone in radar.tracked_drones:
                if drone.health > 20:
                    line = mlines.Line2D(
                        [radar.position[0], drone.position[0]],
                        [radar.position[1], drone.position[1]],
                        color='blue', linestyle='--', linewidth=1.5
                    )
                    self.ax.add_line(line)
                    rec_size = 1/10 * xlim[1]  # 根据坐标轴范围调整大小
                    rect = Rectangle(
                        (drone.position[0] - rec_size/2, drone.position[1] - rec_size/2),
                        rec_size, rec_size,
                        fill=False, color='blue', linewidth=1.5
                    )
                    self.ax.add_patch(rect)

        # 绘制激光
        for laser in lasers:
            self.ax.scatter(laser.position[0], laser.position[1], color='green', marker='^', s=100)
            if laser.target_drone:
                target = laser.target_drone
                line = mlines.Line2D(
                    [laser.position[0], target.position[0]],
                    [laser.position[1], target.position[1]],
                    color='green', linewidth=2
                )
                self.ax.add_line(line)

                if 20 < target.health < 100:
                    outer_radius = 1/20 * xlim[1] * (target.health / 100)
                    inner_radius = outer_radius * 0.7
                    outer_circle = Circle(target.position, outer_radius, color='green', fill=True, alpha=0.3)
                    inner_circle = Circle(target.position, inner_radius, color='white', fill=True)
                    self.ax.add_patch(outer_circle)
                    self.ax.add_patch(inner_circle)
                    
        # 绘制无人机
        for drone in drones:
            if drone.health <= 20:
                self.ax.scatter(drone.position[0], drone.position[1], color='red', marker='x', s=100)
            else:
                self.ax.scatter(drone.position[0], drone.position[1], color='black', marker='o', s=100)