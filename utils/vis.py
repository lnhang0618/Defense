import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.lines as mlines

def plot_drone(drone, ax, color='green'):
    
    max_outer_radius = 1.0
    min_inner_radius_ratio = 0.7  # 内半径占外半径的比例（控制环的宽度）
    
    if drone.health == 100:  # 健康
        ax.scatter(drone.position[0], drone.position[1], color="black", s=100)
    elif 20 < drone.health < 100:
        # 当前 health 比例
        health_ratio = drone.health / 100.0
        
        # 计算当前内外半径
        outer_radius = max_outer_radius * health_ratio
        inner_radius = outer_radius * min_inner_radius_ratio
        
        # 创建圆环（通过两个同心圆叠加）
        outer_circle = Circle(
            drone.position,
            outer_radius,
            color=color,
            fill=True,
            alpha=0.3
        )
        inner_circle = Circle(
            drone.position,
            inner_radius,
            color='white',
            fill=True
        )
        
        # 将圆环添加到坐标轴
        ax.add_patch(outer_circle)
        ax.add_patch(inner_circle)
        
        ax.scatter(drone.position[0], drone.position[1], color="black", s=100)
        
    elif drone.health <= 20:  # 危险
        pass
    
def plot_laser_line(laser, ax, color='green'):
    
    start = laser.position
    end = laser.target.position
    
    ax.scatter(start[0], start[1], color=color, marker='^', s=100)
    
    if laser.target is None or laser.target.health <= 20:
        return
    
    line = mlines.Line2D([start[0], end[0]], [start[1], end[1]], color=color, linewidth=2)
    ax.add_line(line)
    
    