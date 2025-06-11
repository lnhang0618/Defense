from abc import ABC, abstractmethod

class Attacker_Mode_Base(ABC):
    @abstractmethod
    def update(self, radars, lasers, drones, infrastructures):
        '''更新无人机的状态'''
        pass