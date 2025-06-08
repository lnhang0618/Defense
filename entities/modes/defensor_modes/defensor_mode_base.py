from abc import ABC, abstractmethod

class Defensor_Mode_Base(ABC):
    @abstractmethod
    def update(self, radars, lasers, drones):
        '''更新防御者的状态'''
        pass