import os
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WHITE, DARK_GREEN, ROAD_COLOR,
    DIFFICULTIES, HIGHSCORE_FILE,
)


class Road:
    """Scrolling top-down road background."""

    DASH_LEN = 38
    DASH_GAP = 28
    STRIPE_W = 5

    def __init__(self, road_width):
        self.road_width = road_width
        self.road_left = (WINDOW_WIDTH - road_width) // 2
        self.road_right = self.road_left + road_width

        self._tile_h = self.DASH_LEN + self.DASH_GAP
        self._scroll = 0.0
        self._tile = self._build_tile()

    def _build_tile(self):
        tile_h = self._tile_h
        tile = pygame.Surface((WINDOW_WIDTH, tile_h))
        tile.fill(DARK_GREEN)

        # road surface
        pygame.draw.rect(tile, ROAD_COLOR,
                         (self.road_left, 0, self.road_width, tile_h))

        # white edge lines
        pygame.draw.rect(tile, WHITE, (self.road_left, 0, 4, tile_h))
        pygame.draw.rect(tile, WHITE, (self.road_right - 4, 0, 4, tile_h))

        # grass edge strips
        shade = (30, 100, 30)
        for off, sw in [(4, 8), (12, 6)]:
            pygame.draw.rect(tile, shade,
                             (self.road_left - off - sw, 0, sw, tile_h))
            pygame.draw.rect(tile, shade,
                             (self.road_right + off, 0, sw, tile_h))

        # lane dashes (3 lanes)
        num_lanes = 3
        lane_w = self.road_width // num_lanes
        dash_col = (165, 165, 165)
        for i in range(1, num_lanes):
            dx = self.road_left + lane_w * i
            pygame.draw.rect(tile, dash_col,
                             (dx - self.STRIPE_W // 2, 0, self.STRIPE_W, self.DASH_LEN))

        return tile

    def update(self, scroll_speed):
        self._scroll = (self._scroll + scroll_speed) % self._tile_h

    def draw(self, surface):
        y = self._scroll - self._tile_h
        while y < WINDOW_HEIGHT:
            surface.blit(self._tile, (0, int(y)))
            y += self._tile_h


class HighScoreManager:
    def __init__(self):
        self.scores = {k: 0 for k in DIFFICULTIES}
        self._load()

    def _load(self):
        if not os.path.exists(HIGHSCORE_FILE):
            return
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if ":" not in line:
                        continue
                    name, _, val = line.partition(":")
                    if name in self.scores:
                        self.scores[name] = int(val)
        except (ValueError, OSError):
            pass

    def save(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                for name, score in self.scores.items():
                    f.write(f"{name}:{score}\n")
        except OSError:
            pass

    def update(self, difficulty, new_score):
        old = self.scores.get(difficulty, 0)
        if new_score > old:
            self.scores[difficulty] = new_score
            self.save()
            return True
        return False

    def get(self, difficulty):
        return self.scores.get(difficulty, 0)
