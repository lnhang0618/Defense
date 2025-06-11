class Infrastructure:
    def __init__(self, infrastructure_config):
        self.infrastructure_config = infrastructure_config
        self.id = self.infrastructure_config['id']
        self.position = self.infrastructure_config['position']
        
        # 是否被摧毁
        self.destroyed = False