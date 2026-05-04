import random
import pygame
from constants import (
    WINDOW_HEIGHT,
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_COLORS,
)


class EnemyCar(pygame.sprite.Sprite):
    """Enemy car that scrolls down the road.

    When *smart* is True (Medium / Hard difficulty) the car also drifts
    laterally: it picks a random target X within the road bounds and
    steers toward it, re-targeting periodically to create an unpredictable
    weaving pattern that challenges the player.
    """

    # Frames between lateral retargets for smart enemies
    _RETARGET_MIN = 40
    _RETARGET_MAX = 100

    def __init__(self, left_edge, right_edge, move_speed, smart=False):
        super().__init__()
        self.move_speed = move_speed
        self.smart = smart

        # Road boundary kept for lateral clamping
        self._left_edge = left_edge
        self._right_edge = right_edge

        body_color = random.choice(ENEMY_COLORS)

        # slight size variation
        w_off = random.randint(-4, 4)
        h_off = random.randint(-6, 6)
        car_w = ENEMY_WIDTH + w_off
        car_h = ENEMY_HEIGHT + h_off

        self.image = self._make_car(body_color, car_w, car_h)
        self.rect = self.image.get_rect()

        # spawn position
        margin = car_w // 2 + 4
        min_x = left_edge + margin
        max_x = right_edge - margin
        if max_x <= min_x:
            max_x = min_x + 1

        self.rect.centerx = random.randint(min_x, max_x)
        self.rect.bottom = 0

        # --- smart lateral movement state ---
        # Use a float x for smooth sub-pixel motion
        self._float_x = float(self.rect.centerx)
        self._target_x = float(self.rect.centerx)
        self._retarget_timer = 0
        self._retarget_interval = random.randint(
            self._RETARGET_MIN, self._RETARGET_MAX
        )
        # Lateral speed scales with vertical speed so faster enemies also
        # drift faster, keeping the challenge consistent across difficulties.
        self._lateral_speed = max(0.5, move_speed * 0.18)

        # Maximum drift range from current position (pixels)
        self._swerve_range = 40

        if smart:
            self._pick_new_target()

    @staticmethod
    def _make_car(color, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=7)

        # windows
        glass = (190, 225, 255)
        pygame.draw.rect(surf, glass, (6, 7, w - 12, 15), border_radius=4)
        pygame.draw.rect(surf, glass, (6, h - 22, w - 12, 13), border_radius=4)

        # roof stripe
        darker = tuple(max(0, c - 45) for c in color)
        pygame.draw.rect(surf, darker, (w // 2 - 4, 24, 8, h - 48))

        # wheels
        wc = (25, 25, 25)
        for wx, wy in [(-5, 7), (w - 3, 7), (-5, h - 23), (w - 3, h - 23)]:
            pygame.draw.rect(surf, wc, (wx, wy, 8, 16), border_radius=2)

        return surf

    def _pick_new_target(self):
        """Choose a new random X near current position, clamped to road."""
        half_w = self.rect.width // 2 + 4
        road_min = self._left_edge + half_w
        road_max = self._right_edge - half_w
        if road_max <= road_min:
            road_max = road_min + 1

        drift_min = max(road_min, int(self._float_x) - self._swerve_range)
        drift_max = min(road_max, int(self._float_x) + self._swerve_range)
        self._target_x = float(random.randint(drift_min, drift_max))
        self._retarget_interval = random.randint(
            self._RETARGET_MIN, self._RETARGET_MAX
        )
        self._retarget_timer = 0

    def update(self):
        # Vertical movement (always)
        self.rect.y += int(self.move_speed)

        # Lateral movement (smart enemies only)
        if self.smart:
            self._retarget_timer += 1
            if self._retarget_timer >= self._retarget_interval:
                self._pick_new_target()

            # Smoothly drift toward target_x
            diff = self._target_x - self._float_x
            if abs(diff) <= self._lateral_speed:
                self._float_x = self._target_x
            else:
                self._float_x += self._lateral_speed * (1 if diff > 0 else -1)

            # Clamp inside road
            half_w = self.rect.width // 2
            self._float_x = max(
                float(self._left_edge + half_w),
                min(float(self._right_edge - half_w), self._float_x),
            )
            self.rect.centerx = int(self._float_x)

    def is_off_screen(self):
        return self.rect.top > WINDOW_HEIGHT
