class GameManager:
    def __init__(self, config):
        self.config = config
        
        self.world_config = self.config['world']
        
        