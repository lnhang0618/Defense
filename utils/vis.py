import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import matplotlib.lines as mlines
from matplotlib.animation import FFMpegWriter

import numpy as np
import imageio.v3 as imageio

class Visualizer:
    def __init__(self, world_config):
        self.world_config = world_config
        self.fig = None
        self.ax_sim = None
        self.ax_bar = None
        self.writer = None
        self.frames = []
        plt.ion()  # 开启交互模式，允许动态更新图形

    def init_plot(self):
        self.fig, (self.ax_sim, self.ax_bar) = plt.subplots(
            1, 2, figsize=(14, 7), dpi=100,
            gridspec_kw={'width_ratios': [1, 1]}  # 修改此处
        )
        
        # 设置仿真区域
        self.ax_sim.set_xlim(self.world_config['x_bounds'])
        self.ax_sim.set_ylim(self.world_config['y_bounds'])
        self.ax_sim.set_aspect('equal')
        self.ax_sim.set_title("Drone Simulation")
        # self.ax_sim.grid(True)

        # 设置柱状图区域
        self.ax_bar.set_title("Fire Support Analysis")
        self.ax_bar.set_xlabel("Fire Support (units)")
        self.ax_bar.set_ylabel("Radar ID")

    def draw(self, drones, radars, lasers, infrastructures):
        # 清除旧内容
        self.ax_sim.clear()
        self.ax_bar.clear()

        # 恢复坐标轴范围
        self.ax_sim.set_xlim(self.world_config['x_bounds'])
        self.ax_sim.set_ylim(self.world_config['y_bounds'])
        self.ax_sim.set_title("Drone Simulation")
        # self.ax_sim.grid(True)

        # 绘制雷达
        for radar in radars:
            self.ax_sim.scatter(radar.position[0], radar.position[1], color='blue', marker='s', s=100)

            outer_circle = Circle(radar.position, radar.radius, color='gray', fill=True, linestyle='--', linewidth=1.5, alpha=0.3)
            self.ax_sim.add_patch(outer_circle)

            for drone in radar.tracked_drones:
                if drone.health > 20:
                    line = mlines.Line2D(
                        [radar.position[0], drone.position[0]],
                        [radar.position[1], drone.position[1]],
                        color='blue', linestyle='--', linewidth=1.5
                    )
                    self.ax_sim.add_line(line)
                    rec_size = 1/10 * self.world_config['x_bounds'][1]
                    rect = Rectangle(
                        (drone.position[0] - rec_size/2, drone.position[1] - rec_size/2),
                        rec_size, rec_size,
                        fill=False, color='blue', linewidth=1.5
                    )
                    self.ax_sim.add_patch(rect)

        # 绘制激光
        for laser in lasers:
            self.ax_sim.scatter(laser.position[0], laser.position[1], color='green', marker='^', s=100)
            if laser.target_drone and not laser.target_drone.destroyed:
                target = laser.target_drone
                line = mlines.Line2D(
                    [laser.position[0], target.position[0]],
                    [laser.position[1], target.position[1]],
                    color='green', linewidth=2
                )
                self.ax_sim.add_line(line)

                if 20 < target.health < 100:
                    outer_radius = 1 / 20 * self.world_config['x_bounds'][1] * (target.health / 100)
                    inner_radius = outer_radius * 0.7
                    outer_circle = Circle(target.position, outer_radius, color='green', fill=True, alpha=0.3)
                    inner_circle = Circle(target.position, inner_radius, color='white', fill=True)
                    self.ax_sim.add_patch(outer_circle)
                    self.ax_sim.add_patch(inner_circle)
                    
            if laser.coorperate_radar and not laser.target_drone.destroyed:
                radar = laser.coorperate_radar
                line = mlines.Line2D(
                    [laser.position[0], radar.position[0]],
                    [laser.position[1], radar.position[1]],
                    color='blue', linestyle='--', linewidth=1.5
                )
                self.ax_sim.add_line(line)

        # 绘制无人机
        for drone in drones:
            if drone.destroyed or drone.succeed:
                # self.ax_sim.scatter(drone.position[0], drone.position[1], color='red', marker='x', s=100)
                continue
            else:
                self.ax_sim.scatter(drone.position[0], drone.position[1], color='black', marker='o', s=100, alpha=0.7)
                
        # 绘制基础设施
        for infra in infrastructures:
            if infra.destroyed:
                self.ax_sim.scatter(infra.position[0], infra.position[1], color='red', marker='x', s=100)
            else:
                self.ax_sim.scatter(infra.position[0], infra.position[1], marker='s', color='black', facecolors='none', s=100)

        # 绘制窗口期柱状图
        self.draw_fire_support(drones,radars,lasers)
        
        # 添加无人机统计信息
        total_drones = len(drones)
        destroyed_drones = sum(1 for drone in drones if drone.destroyed)
        alive_drones = total_drones - destroyed_drones

        # 在左上角显示文本
        textstr = f"Total Drones: {total_drones}\nAlive: {alive_drones}\nDestroyed: {destroyed_drones}"
        self.ax_sim.text(0.02, 0.95, textstr, transform=self.ax_sim.transAxes, fontsize=12,
                        verticalalignment='top', bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))

        plt.draw()
        plt.pause(0.2)  # 短暂暂停以更新图形界面

    def draw_fire_support(self, drones, radars, lasers):
        radar_fire_support = {radar.radar_id: {"required": 0, "available": 0} for radar in radars}

        # 收集窗口期数据
        for radar in radars:
            if len(radar.tracked_drones) == 0:
                continue
            required_fire_support = 0
            for drone_id, period in radar.drone_window_periods_dict.items():
                required_fire_support += (drones[drone_id].health-20) / period
                
            radar_fire_support[radar.radar_id]["required"] = required_fire_support
            
            available_fire_support = 0
            for laser in radar.cooperate_lasers:
                available_fire_support += laser.get_effective_rate()
                
            radar_fire_support[radar.radar_id]["available"] = available_fire_support


        # 清除并重新绘制柱状图
        self.ax_bar.clear()
        self.ax_bar.set_title("Fire Support Analysis")
        self.ax_bar.set_xlabel("Fire Support (units)")
        self.ax_bar.set_ylabel("Radar ID")
        self.ax_bar.set_xlim(0, 100)  # 设置 x 轴范围

        # 准备双柱图数据
        y_positions = np.arange(len(radar_fire_support))
        required_support = [radar_fire_support[radar_id]["required"] for radar_id in radar_fire_support]
        available_support = [radar_fire_support[radar_id]["available"] for radar_id in radar_fire_support]
        
        # 绘制双柱图
        self.ax_bar.barh(
            y=y_positions - 0.15,
            width=required_support,
            height=0.3,
            color='skyblue',
            label='Required Fire Support'
        )
        self.ax_bar.barh(
            y=y_positions + 0.15,
            width=available_support,
            height=0.3,
            color='orange',
            label='Available Fire Support'
        )

        # 固定 y 轴范围
        self.ax_bar.set_ylim(-0.5, len(radar_fire_support) - 0.5)
        self.max_bar_limit = 100
        
        # 设置 y 轴标签
        ytick_labels = [f"Radar {radar_id}" for radar_id in radar_fire_support]
        self.ax_bar.set_yticks(y_positions)
        self.ax_bar.set_yticklabels(ytick_labels)

        # 固定 x 轴范围
        if self.max_bar_limit > 0:
            self.ax_bar.set_xlim(0, self.max_bar_limit * 1.1)

        # 添加图例
        self.ax_bar.legend(loc='upper right')

        # 防止标签挤占图表区域
        # self.fig.subplots_adjust(left=0.25)

    def record_frame(self):
        """将当前帧保存为图像并缓存"""
        # 将当前图像转换为 RGB 格式并存储
        self.fig.canvas.draw()
        image = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
        
        # import matplotlib.image as mpimg
        # mpimg.imsave('current_frame.png', image)  # 保存当前帧为 PNG 文件（可选）
        
        self.frames.append(image)

    def save_video(self, output_file="simulation.mp4", fps=10):
        if not self.frames:
            print("No frames to save.")
            return

        try:
            with imageio.imopen(output_file, "w", plugin="pyav") as file:
                # 初始化视频流，使用 libx264 编码器
                file.init_video_stream("libx264", fps=fps)

                for i, frame in enumerate(self.frames):
                    file.write_frame(frame)
                    if i % 10 == 0:
                        print(f"Saving frame {i} / {len(self.frames)}")

            print(f"Video saved to {output_file}")
        except Exception as e:
            print("Error saving video:", e)