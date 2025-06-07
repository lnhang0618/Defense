from managers.game_manager import GameManager

config_path = "/home/newuser/robot/defense/configs/test_config.yaml"

game_manager = GameManager(config_path)

game_manager.start_simulation()