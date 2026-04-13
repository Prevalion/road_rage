# shared config / constants

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
TITLE = "Road Rage"

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
ROAD_COLOR = (55, 55, 55)
LANE_COLOR = (255, 255, 255)
GRASS_COLOR = (34, 139, 34)
DARK_GREEN = (20, 80, 20)
ORANGE = (255, 140, 0)
CYAN = (0, 210, 230)
PINK = (255, 100, 150)

# game states
STATE_MENU = "MENU"
STATE_DIFFICULTY = "DIFFICULTY_SELECT"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"

# difficulty configs
DIFFICULTIES = {
    "Easy": {
        "label": "Easy — Level 1",
        "road_width": 500,
        "enemy_speed": 3.0,
        "speed_increment": 0.5,
        "speed_interval": 15,
        "spawn_rate": 90,
        "lives": 3,
        "powerups": True,
        "heart_interval": 10,
        "shield_interval": 15,
    },
    "Medium": {
        "label": "Medium — Level 2",
        "road_width": 380,
        "enemy_speed": 5.0,
        "speed_increment": 0.7,
        "speed_interval": 12,
        "spawn_rate": 60,
        "lives": 3,
        "powerups": False,
    },
    "Hard": {
        "label": "Hard — Level 3",
        "road_width": 260,
        "enemy_speed": 8.0,
        "speed_increment": 1.0,
        "speed_interval": 8,
        "spawn_rate": 40,
        "lives": 1,
        "powerups": False,
    },
}

# player
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 65
PLAYER_SPEED = 5
PLAYER_COLOR = (30, 100, 255)

# enemy
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 65

ENEMY_COLORS = [
    (220, 50, 50),
    (200, 100, 0),
    (150, 0, 150),
    (0, 140, 80),
    (180, 160, 0),
    (200, 60, 120),
    (70, 130, 180),
    (255, 165, 0),
    (138, 43, 226),
    (34, 139, 34),
    (255, 215, 0),
    (128, 0, 128),
    (0, 191, 255),
    (220, 20, 60),
    (75, 0, 130),
]

# powerups
POWERUP_WIDTH = 32
POWERUP_HEIGHT = 32

SHIELD_DURATION = 5 * FPS   # frames
SHIELD_FLASH_SECS = 2

FLASH_DURATION = 30

HIGHSCORE_FILE = "highscores.txt"
