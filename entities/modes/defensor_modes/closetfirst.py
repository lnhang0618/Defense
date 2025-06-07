from utils.utils import cal_distance
from entities.modes.defensor_modes.defensor_mode_base import Defensor_Mode_Base
from copy import deepcopy

class ClosestFirst(Defensor_Mode_Base):
    def update_defensors(self, radars, lasers, drones):
        # 阶段一：更新雷达检测状态
        for radar in radars:
            radar.detect_drones(drones)

        # 阶段二：分配雷达跟踪目标
        self.assign_radars_to_targets(radars, lasers, drones)

        # 阶段三：分配激光攻击目标
        self.assign_lasers_to_targets(radars, lasers)

    def assign_radars_to_targets(self, radars, lasers, drones):
        """
        雷达根据激光锁定状态选择跟踪目标。
        """
        # 获取所有被激光锁定的目标
        active_targets = [l.target_drone for l in lasers if l.target_drone is not None]
        
        # 为每个雷达分配跟踪目标
        for radar in radars:
            # 已经跟踪的目标
            current_tracks = set(radar.tracked_drones)
            
            # 可探测的无人机
            in_range = [d for d in drones if cal_distance(radar.position, d.position) <= radar.radius]
            in_range.sort(key=lambda d: cal_distance(radar.position, d.position))

            # 1. 优先确保 active_targets 被跟踪
            targets_to_track = []
            for drone in active_targets:
                if drone in in_range and drone not in radar.tracked_drones:
                    targets_to_track.append(drone)
                    if len(targets_to_track) >= radar.max_tracks:
                        break

            # 2. 剩余名额分配给其他未被锁定的无人机
            unassigned = [d for d in in_range if d not in active_targets]
            for drone in unassigned:
                if drone not in targets_to_track and len(targets_to_track) < radar.max_tracks:
                    targets_to_track.append(drone)

            # 更新雷达跟踪目标
            new_tracks = set(targets_to_track)
            removed = current_tracks - new_tracks
            added = new_tracks - current_tracks

            # 更新无人机的锁定状态
            for drone in removed:
                if radar in drone.locked_radars:
                    drone.locked_radars.remove(radar)

            for drone in added:
                drone.locked_radars.append(radar)

            radar.tracked_drones = list(new_tracks)

    def assign_lasers_to_targets(self, radars, lasers):
        """
        激光炮在雷达锁定的目标中选择攻击目标。
        """
        # 获取所有雷达锁定的目标
        tracked_drones = set()
        for radar in radars:
            tracked_drones.update(radar.tracked_drones)

        # 获取当前被激光锁定的目标
        active_targets = [l.target_drone for l in lasers if l.target_drone is not None]

        # 分配新目标
        for laser in lasers:
            if laser.target_drone is not None:
                # 已有目标，检查是否仍被雷达跟踪
                if laser.target_drone not in tracked_drones:
                    laser.target_drone = None
                else:
                    continue

            # 寻找新目标：未被其他激光锁定、且被雷达跟踪
            candidates = [d for d in tracked_drones if d not in active_targets]
            if candidates:
                candidates.sort(key=lambda d: cal_distance(laser.position, d.position))
                laser.target_drone = candidates[0]
                active_targets.append(laser.target_drone)
            else:
                laser.target_drone = None

            # 更新激光状态
            laser.attack_drone()