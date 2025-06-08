from abc import ABC, abstractmethod

class Attacker_Mode_Base(ABC):
    @abstractmethod
    def update(self, radars, lasers, drones):
        '''更新无人机的方向'''
        pass