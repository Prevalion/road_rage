import random
import pygame
from constants import (
    WINDOW_HEIGHT,
    POWERUP_WIDTH, POWERUP_HEIGHT,
    RED, CYAN, WHITE,
)


class Powerup(pygame.sprite.Sprite):

    DRIFT_SPEED = 2

    def __init__(self, pickup_type, left_edge, right_edge):
        super().__init__()
        self.powerup_type = pickup_type
        self.image = self._make_icon(pickup_type)
        self.rect = self.image.get_rect()

        margin = POWERUP_WIDTH // 2 + 4
        min_x = left_edge + margin
        max_x = right_edge - margin
        if max_x <= min_x:
            max_x = min_x + 1

        self.rect.centerx = random.randint(min_x, max_x)
        self.rect.bottom = 0

    @staticmethod
    def _make_icon(pickup_type):
        surf = pygame.Surface((POWERUP_WIDTH, POWERUP_HEIGHT), pygame.SRCALPHA)
        cx = POWERUP_WIDTH // 2
        cy = POWERUP_HEIGHT // 2

        if pickup_type == "heart":
            r = POWERUP_WIDTH // 4
            pygame.draw.circle(surf, RED, (cx - r + 1, cy - 2), r + 2)
            pygame.draw.circle(surf, RED, (cx + r - 1, cy - 2), r + 2)
            pygame.draw.polygon(surf, RED, [
                (2, cy + 1),
                (POWERUP_WIDTH - 2, cy + 1),
                (cx, POWERUP_HEIGHT - 2),
            ])
            # highlight
            pygame.draw.circle(surf, (255, 180, 180), (cx - r + 2, cy - 4), r // 2)

        elif pickup_type == "shield":
            pts = [
                (cx, 2),
                (POWERUP_WIDTH - 3, cy - 4),
                (POWERUP_WIDTH - 3, cy + 4),
                (cx, POWERUP_HEIGHT - 2),
                (3, cy + 4),
                (3, cy - 4),
            ]
            pygame.draw.polygon(surf, CYAN, pts)
            pygame.draw.polygon(surf, WHITE, pts, 2)
            # lightning bolt
            pygame.draw.line(surf, WHITE, (cx + 2, 6), (cx - 3, cy), 2)
            pygame.draw.line(surf, WHITE, (cx - 3, cy), (cx + 2, cy), 2)
            pygame.draw.line(surf, WHITE, (cx + 2, cy), (cx - 3, POWERUP_HEIGHT - 6), 2)

        return surf

    def update(self):
        self.rect.y += self.DRIFT_SPEED

    def is_off_screen(self):
        return self.rect.top > WINDOW_HEIGHT
