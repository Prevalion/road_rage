import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_COLOR,
    SHIELD_DURATION, SHIELD_FLASH_SECS, FLASH_DURATION,
    RED, CYAN, WHITE, DARK_GRAY,
)


class Player(pygame.sprite.Sprite):

    def __init__(self, left_bound, right_bound):
        super().__init__()
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.speed = PLAYER_SPEED

        self._base_sprite = self._make_car(PLAYER_COLOR)
        self.image = self._base_sprite.copy()
        self.rect = self.image.get_rect(
            centerx=WINDOW_WIDTH // 2,
            bottom=WINDOW_HEIGHT - 30,
        )

        self.shield_active = False
        self.shield_timer = 0
        self._flashing = False
        self._flash_timer = 0

    @staticmethod
    def _make_car(body_color):
        surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

        pygame.draw.rect(surf, body_color,
                         (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT), border_radius=7)

        # windshield + rear window
        glass = (190, 225, 255)
        pygame.draw.rect(surf, glass,
                         (6, 7, PLAYER_WIDTH - 12, 15), border_radius=4)
        pygame.draw.rect(surf, glass,
                         (6, PLAYER_HEIGHT - 22, PLAYER_WIDTH - 12, 13), border_radius=4)

        stripe = tuple(max(0, c - 40) for c in body_color)
        pygame.draw.rect(surf, stripe,
                         (PLAYER_WIDTH // 2 - 4, 24, 8, PLAYER_HEIGHT - 48))

        wc = (25, 25, 25)
        for wx, wy in [(-5, 7), (PLAYER_WIDTH - 3, 7),
                        (-5, PLAYER_HEIGHT - 23), (PLAYER_WIDTH - 3, PLAYER_HEIGHT - 23)]:
            pygame.draw.rect(surf, wc, (wx, wy, 8, 16), border_radius=2)

        return surf

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = SHIELD_DURATION

    def block_hit_with_shield(self):
        self.shield_active = False
        self.shield_timer = 0

    def take_hit(self):
        self._flashing = True
        self._flash_timer = FLASH_DURATION

    def update(self, pressed):
        # movement (arrows + wasd)
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.rect.x += self.speed
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            self.rect.y -= self.speed
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            self.rect.y += self.speed

        # clamp to road
        self.rect.left = max(self.left_bound, self.rect.left)
        self.rect.right = min(self.right_bound, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(WINDOW_HEIGHT, self.rect.bottom)

        # shield countdown
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                self.shield_timer = 0

        # flash countdown
        if self._flashing:
            self._flash_timer -= 1
            if self._flash_timer <= 0:
                self._flashing = False
                self._flash_timer = 0

        # update sprite visual
        self._refresh_image()

    def _refresh_image(self):
        shield_flash_frames = SHIELD_FLASH_SECS * FPS

        if self._flashing and (self._flash_timer // 5) % 2 == 0:
            self.image = self._make_car(RED)
        elif self.shield_active:
            about_to_expire = self.shield_timer <= shield_flash_frames
            blink = (self.shield_timer // 6) % 2 == 0
            if about_to_expire and blink:
                self.image = self._make_car(WHITE)
            else:
                self.image = self._make_car(CYAN)
        else:
            self.image = self._base_sprite.copy()
