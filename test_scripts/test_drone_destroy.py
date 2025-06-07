import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
from entities.drone import Drone
from entities.laser import Laser
from entities.radar import Radar  # 假设 Radar 类已经定义
from utils.vis import plot_drone, plot_laser_tracking, plot_radar_tracking
    

# 示例：测试函数
if __name__ == "__main__":
    # 创建一个简单的无人机对象
    class Config:
        world = {'x_bounds': (0, 10), 'y_bounds': (0, 10)}
        drone = {'speed': 1}
        laser = {'id': 1, 'position': (1, 1), 'radius': 10}
        lader = {'id': 1, 'position': (5, 3), 'radius': 5, 'max_tracks': 2}
    
    drone = Drone(Config.world, Config.drone)
    laser = Laser(Config.laser)
    lader = Radar(Config.lader)  # 假设 Radar 类已经定义
    laser.target = drone  # 设置激光目标为无人机
    lader.tracked_drones.append(drone)  # 假设雷达追踪了这个无人机
    drone.drone_id = 1
    drone.position = (5, 5)  # 初始位置
    drone.health = 50        # 初始健康值

    # 创建绘图环境
    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')  # 确保 x 和 y 轴比例一致

    # 模拟 health 逐渐降低
    for health in range(100, 0, -10):
        drone.health = health
        # plot_drone(drone, ax, color='green')
        plot_radar_tracking(lader, ax, color='blue')
        plot_laser_tracking(laser, ax, color='green')
        plot_drone(drone, ax)
        plt.pause(1)  # 暂停 1 秒观察效果
        ax.clear()    # 清除当前画面
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')

    plt.show()