import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    WHITE, YELLOW, RED, CYAN, DARK_GRAY,
    SHIELD_DURATION, SHIELD_FLASH_SECS,
)


def _load_fonts():
    names = ["Arial", "Helvetica", "DejaVu Sans", "FreeSans", ""]
    sizes = [30, 22, 18, 15]
    result = []
    for sz in sizes:
        loaded = False
        for name in names:
            try:
                if name:
                    f = pygame.font.SysFont(name, sz, bold=(sz >= 22))
                else:
                    f = pygame.font.Font(None, sz + 4)
                result.append(f)
                loaded = True
                break
            except Exception:
                continue
        if not loaded:
            result.append(pygame.font.Font(None, sz + 4))
    return tuple(result)


class HUD:

    def __init__(self, max_lives, difficulty_text):
        self.max_lives = max_lives
        self.difficulty_text = difficulty_text
        self.current_lives = max_lives
        self.current_score = 0
        self.high_score = 0
        self.shield_active = False
        self.shield_timer = 0
        self._shield_max = SHIELD_DURATION

        self._font_big, self._font_med, self._font_sm, self._font_xs = _load_fonts()

    def update(self, lives, score, high_score, shield_active, shield_timer):
        self.current_lives = lives
        self.current_score = score
        self.high_score = high_score
        self.shield_active = shield_active
        self.shield_timer = shield_timer

    def draw(self, surface):
        self._draw_hearts(surface)
        self._draw_score(surface)
        self._draw_diff_label(surface)
        if self.shield_active:
            self._draw_shield_bar(surface)

    def _draw_hearts(self, surface):
        x = 12
        y = 12
        for i in range(self.max_lives):
            filled = i < self.current_lives
            self._draw_heart(surface, x, y, filled)
            x += 32

    @staticmethod
    def _draw_heart(surface, x, y, filled):
        size = 24
        mid = x + size // 2
        bump_r = size // 4
        color = RED if filled else DARK_GRAY

        pygame.draw.circle(surface, color, (mid - bump_r + 1, y + bump_r - 1), bump_r + 1)
        pygame.draw.circle(surface, color, (mid + bump_r - 1, y + bump_r - 1), bump_r + 1)
        pygame.draw.polygon(surface, color, [
            (x + 1, y + bump_r + 1),
            (x + size - 1, y + bump_r + 1),
            (mid, y + size - 1),
        ])
        if filled:
            pygame.draw.circle(surface, (255, 160, 160),
                               (mid - bump_r + 3, y + bump_r - 2), bump_r // 2)

    def _draw_score(self, surface):
        score_surf = self._font_big.render(f"Score: {self.current_score}", True, WHITE)
        best_surf = self._font_sm.render(f"Best: {self.high_score}", True, YELLOW)
        surface.blit(score_surf, (WINDOW_WIDTH - score_surf.get_width() - 10, 10))
        surface.blit(best_surf, (WINDOW_WIDTH - best_surf.get_width() - 10, 44))

    def _draw_diff_label(self, surface):
        label = self._font_xs.render(self.difficulty_text, True, (190, 190, 190))
        surface.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, 12))

    def _draw_shield_bar(self, surface):
        bar_w = 200
        bar_h = 12
        bx = WINDOW_WIDTH // 2 - bar_w // 2
        by = WINDOW_HEIGHT - 34

        # background track
        pygame.draw.rect(surface, (30, 30, 30),
                         (bx - 2, by - 2, bar_w + 4, bar_h + 4), border_radius=4)

        fill_pct = max(0.0, self.shield_timer / self._shield_max)
        fill_w = int(bar_w * fill_pct)

        flash_point = SHIELD_FLASH_SECS * FPS
        expiring = self.shield_timer <= flash_point
        blink = (self.shield_timer // 6) % 2 == 0
        bar_color = (255, 255, 255) if (expiring and blink) else CYAN

        if fill_w > 0:
            pygame.draw.rect(surface, bar_color,
                             (bx, by, fill_w, bar_h), border_radius=3)

        lbl = self._font_xs.render("SHIELD", True, CYAN)
        surface.blit(lbl, (WINDOW_WIDTH // 2 - lbl.get_width() // 2, by - 18))
