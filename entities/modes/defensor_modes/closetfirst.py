from utils.utils import cal_distance
from entities.modes.defensor_modes.defensor_mode_base import Defensor_Mode_Base
import numpy as np
from scipy.optimize import linear_sum_assignment

class ClosestFirst(Defensor_Mode_Base):
    def __init__(self, assignment_strategy='minsum'):
        self.assignment_strategy = assignment_strategy
    
    def update(self, radars, lasers, drones, infrastructures):
        # 阶段一：清理状态（移除已逃脱或被击毁的无人机）
        # 以及判断无人机是否可以被检测，并根据规则更新雷达和激光炮的状态
        self.reset_state(radars, lasers, drones)
        
        # 阶段三：分配雷达跟踪目标（优先保障被激光锁定的目标）
        self.assign_radars_to_active_targets(radars, lasers, drones)
        
        # 阶段四：优化分配剩余资源
        self.optimize_resource_allocation(radars, lasers, drones)
        
        # 阶段五：更新激光状态
        for laser in lasers:
            laser.attack_drone()
    
    def reset_state(self, radars, lasers, drones):
        """清理无效状态：已逃脱/被击毁的无人机"""
        # 重置无人机的检测和锁定状态
        for drone in drones:
            drone.detected_by_radar = False
            drone.locked_by_radar = False
        
        # 清理雷达跟踪列表
        for radar in radars:
            # 检测每个radar可检测的无人机
            radar.detect_drones(drones)
            # 保留未逃脱且未被击毁的无人机
            valid_drones = [d for d in radar.tracked_drones if not d.succeed and not d.destroyed and d.detected_by_radar]
            radar.tracked_drones = valid_drones
            # 清理雷达的协作激光炮
            valid_lasers = [l for l in radar.cooperate_lasers if l.target_drone and not l.target_drone.succeed and not l.target_drone.destroyed]
            radar.cooperate_lasers = valid_lasers
            
            for drone in valid_drones:
                drone.locked_by_radar = True
                
        # 清理激光目标
        for laser in lasers:
            if laser.target_drone:
            # 如果激光目标无人机已被雷达解除锁定、逃脱或被击毁，则清除激光目标
                if (not laser.target_drone.locked_by_radar or 
                    laser.target_drone.succeed or 
                    laser.target_drone.destroyed):
                    laser.target_drone = None
                    laser.coorperate_radar = None
    
    def assign_radars_to_active_targets(self, radars, lasers, drones):
        """当前版本锁定雷达与激光炮的分配直到激光炮目标被击毁或逃脱"""
        
        # 当前不涉及再分配，该步骤可以暂时省略
        pass 
    
    def optimize_resource_allocation(self, radars, lasers, drones):
        # 获取空闲激光炮和可分配无人机
        free_lasers = [l for l in lasers if l.target_drone is None]
        allocatable_drones = [d for d in drones 
                            if not d.succeed and not d.destroyed and 
                            not any(l.target_drone == d for l in lasers)]
        
        # 计算雷达剩余容量
        radar_capacities = {}
        for radar in radars:
            remaining = radar.max_tracks - len(radar.tracked_drones)
            radar_capacities[radar.radar_id] = max(0, remaining)  # 确保非负
        
        # 构建可攻击无人机集合（有雷达覆盖的）
        attackable_drones = [
            d for d in allocatable_drones
            if not d.locked_by_radar
            and any(d in radar.detected_drones for radar in radars)
        ]
        
        # 如果没有空闲激光炮或可攻击的无人机，则不进行分配
        if not free_lasers or not attackable_drones:
            return
        
        # 计算每个无人机的预期生存时间，转化为火力支援强度
        drone_required_fire_support = {drone.drone_id: 0 for drone in attackable_drones}
        for radar in radars:
            for drone_id, period in radar.drone_window_periods_dict.items():
                drone_required_fire_support[drone_id] = (drones[drone_id].health - 20) / period

        # 构建距离矩阵（激光炮×无人机）
        dist_matrix = np.zeros((len(free_lasers), len(attackable_drones)))
        for i, laser in enumerate(free_lasers):
            for j, drone in enumerate(attackable_drones):
                
                # 获取激光炮和无人机之间的有效火力强度
                effective_rate = laser.get_effective_rate(drone)
                if effective_rate < drone_required_fire_support[drone.drone_id]:
                    # 如果激光炮的火力不足以满足无人机的需求，则设置距离为较大值
                    dist_matrix[i, j] = 1e4
                else:
                    dist_matrix[i, j] = cal_distance(laser.position, drone.position)
        
        # 求解最小化最大距离的分配
        if self.assignment_strategy == 'minmax':
            laser_assignments, drone_assignments = self.minmax_assignment(
                dist_matrix, 
                free_lasers,
                attackable_drones,
                radar_capacities
            )
        elif self.assignment_strategy == 'minsum':  # 新增minsum分支
            laser_assignments, drone_assignments = self.minsum_assignment(
                dist_matrix,
                free_lasers,
                attackable_drones,
                radar_capacities
            )
        
        # 应用分配结果
        for lidx, didx in zip(laser_assignments, drone_assignments):
            laser = free_lasers[lidx]
            drone = attackable_drones[didx]
            
            # 查找可用雷达
            for radar in radars:
                if (radar_capacities[radar.radar_id] > 0 and 
                    drone in radar.detected_drones):
                    # 分配雷达
                    radar.lock_on_drone(drone)
                    radar.cooperate_lasers.append(laser)
                    drone.locked_by_radar = True
                    radar_capacities[radar.radar_id] -= 1
                    # 分配激光
                    laser.target_drone = drone
                    laser.coorperate_radar = radar
                    break

    def minmax_assignment(self, dist_matrix, lasers, drones, radar_capacities):
        """最小化最大距离的分配算法"""
        # 获取距离的排序范围
        min_dist = np.min(dist_matrix)
        max_dist = np.max(dist_matrix)
        
        # 二分搜索最小可行最大距离
        best_assignment = None
        while max_dist - min_dist > 1e-5:
            mid = (min_dist + max_dist) / 2
            if self.is_feasible(dist_matrix, mid, lasers, drones, radar_capacities):
                max_dist = mid
            else:
                min_dist = mid
        
        # 构造二分图 (距离<=max_dist)
        n_lasers, n_drones = dist_matrix.shape
        bipartite_graph = np.zeros((n_lasers, n_drones))
        for i in range(n_lasers):
            for j in range(n_drones):
                if dist_matrix[i, j] <= max_dist:
                    bipartite_graph[i, j] = 1
        
        # 求解最大匹配
        laser_inds, drone_inds = linear_sum_assignment(-bipartite_graph)
        return laser_inds, drone_inds
    
    def minsum_assignment(self, dist_matrix, lasers, drones, radar_capacities):
        """最小化总距离的分配算法"""
        # 求解最小总距离分配
        laser_inds, drone_inds = linear_sum_assignment(dist_matrix)
        
        # 按距离排序匹配对（优先保留小距离）
        matches = []
        for lidx, didx in zip(laser_inds, drone_inds):
            dist = dist_matrix[lidx, didx]
            matches.append((lidx, didx, dist))
        matches.sort(key=lambda x: x[2])  # 按距离升序排序
        
        # 根据雷达容量截断匹配
        available_radars = sum(radar_capacities.values())
        valid_matches = matches[:available_radars]
        
        # 分离索引
        laser_assignments = [m[0] for m in valid_matches]
        drone_assignments = [m[1] for m in valid_matches]
        return laser_assignments, drone_assignments

    def is_feasible(self, dist_matrix, max_dist, lasers, drones, radar_capacities):
        """检查给定最大距离是否可行"""
        # 构造二分图 (距离<=max_dist)
        n_lasers, n_drones = dist_matrix.shape
        bipartite_graph = np.zeros((n_lasers, n_drones))
        for i in range(n_lasers):
            for j in range(n_drones):
                if dist_matrix[i, j] <= max_dist:
                    bipartite_graph[i, j] = 1
        
        # 求解最大匹配
        row_inds, col_inds = linear_sum_assignment(-bipartite_graph)
        matched_drones = set(col_inds)
        
        # 检查雷达容量是否满足
        required_radars = len(matched_drones)
        available_radars = sum(radar_capacities.values())
        return available_radars >= required_radars