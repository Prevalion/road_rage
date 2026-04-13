import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WHITE, BLACK, RED, GREEN, YELLOW, GRAY, CYAN, DARK_GREEN, ROAD_COLOR,
    DIFFICULTIES,
)


def _load_font(size, bold=False):
    for name in ("Arial", "Helvetica", "DejaVu Sans", "FreeSans"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size + 4)


class UIRenderer:
    """Handles all non-gameplay screen drawing: menus, overlays, difficulty select."""

    _MENU_DASH_H = 38
    _MENU_DASH_GAP = 28
    _MENU_TILE_H = _MENU_DASH_H + _MENU_DASH_GAP

    BTN_W = 300
    BTN_H = 76

    def __init__(self):
        self.font_title  = _load_font(54, bold=True)
        self.font_large  = _load_font(36, bold=True)
        self.font_medium = _load_font(28)
        self.font_small  = _load_font(22)
        self.font_tiny   = _load_font(17)

    # ------------------------------------------------------------------
    # Menu road background
    # ------------------------------------------------------------------

    def draw_menu_road(self, surface, menu_scroll):
        surface.fill(DARK_GREEN)
        road_w = 340
        rx = WINDOW_WIDTH // 2 - road_w // 2

        pygame.draw.rect(surface, ROAD_COLOR, (rx, 0, road_w, WINDOW_HEIGHT))
        pygame.draw.rect(surface, WHITE, (rx, 0, 4, WINDOW_HEIGHT))
        pygame.draw.rect(surface, WHITE, (rx + road_w - 4, 0, 4, WINDOW_HEIGHT))

        tile_h = self._MENU_TILE_H
        dash_h = self._MENU_DASH_H
        scroll = int(menu_scroll) % tile_h
        cx = rx + road_w // 2 - 3
        y = -tile_h + scroll
        while y < WINDOW_HEIGHT:
            pygame.draw.rect(surface, (165, 165, 165), (cx, y, 6, dash_h))
            y += tile_h

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def draw_menu(self, surface, menu_scroll):
        self.draw_menu_road(surface, menu_scroll)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        title  = self.font_title.render("ROAD RAGE", True, RED)
        shadow = self.font_title.render("ROAD RAGE", True, (80, 0, 0))
        tx = WINDOW_WIDTH // 2 - title.get_width() // 2
        surface.blit(shadow, (tx + 3, 148))
        surface.blit(title,  (tx, 145))

        tagline = self.font_small.render("Infinite Car Dodge", True, (200, 200, 200))
        surface.blit(tagline, (WINDOW_WIDTH // 2 - tagline.get_width() // 2, 212))

        if (pygame.time.get_ticks() // 550) % 2 == 0:
            prompt = self.font_medium.render("Press ENTER to Start", True, YELLOW)
            surface.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 320))

        hints = [
            ("← → / A D", "Move left / right"),
            ("↑ ↓ / W S", "Move up / down"),
            ("P  /  ESC",  "Pause game"),
            ("R",          "Retry after game over"),
            ("Q",          "Quit"),
        ]
        hy = 395
        for key_lbl, desc in hints:
            ks = self.font_tiny.render(key_lbl, True, YELLOW)
            ds = self.font_tiny.render(f"  —  {desc}", True, (170, 170, 170))
            total = ks.get_width() + ds.get_width()
            sx = WINDOW_WIDTH // 2 - total // 2
            surface.blit(ks, (sx, hy))
            surface.blit(ds, (sx + ks.get_width(), hy))
            hy += 22

    # ------------------------------------------------------------------
    # Difficulty select
    # ------------------------------------------------------------------

    def diff_buttons(self):
        buttons = {}
        for i, key in enumerate(("Easy", "Medium", "Hard")):
            bx = WINDOW_WIDTH // 2 - self.BTN_W // 2
            by = 210 + i * 100
            buttons[key] = pygame.Rect(bx, by, self.BTN_W, self.BTN_H)
        return buttons

    def draw_difficulty(self, surface, menu_scroll, hover_btn, score_mgr):
        self.draw_menu_road(surface, menu_scroll)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        header = self.font_large.render("Select Difficulty", True, WHITE)
        surface.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, 140))

        btn_info = {
            "Easy":   (GREEN,  "3 lives · Powerups enabled · Slower start"),
            "Medium": (YELLOW, "3 lives · No powerups  · Faster start  · Smart enemies"),
            "Hard":   (RED,    "1 life  · No powerups  · Maximum speed · Smart enemies"),
        }

        for dk, rect in self.diff_buttons().items():
            accent, subtitle = btn_info[dk]
            hovered = hover_btn == dk

            bg = tuple(min(255, c + 55) for c in accent) if hovered \
                 else tuple(max(0, c - 70) for c in accent)

            pygame.draw.rect(surface, bg, rect, border_radius=11)
            pygame.draw.rect(surface, accent, rect, 3, border_radius=11)

            label = self.font_medium.render(DIFFICULTIES[dk]["label"], True, WHITE)
            surface.blit(label, (rect.centerx - label.get_width() // 2, rect.y + 10))

            sub = self.font_tiny.render(subtitle, True, (210, 210, 210))
            surface.blit(sub, (rect.centerx - sub.get_width() // 2, rect.y + 44))

            best   = score_mgr.get(dk)
            best_s = self.font_tiny.render(f"Best: {best}", True, YELLOW)
            surface.blit(best_s, (rect.right - best_s.get_width() - 8, rect.y + 10))

        hint = self.font_tiny.render("Keys  1 / 2 / 3  or click a button", True, GRAY)
        surface.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 558))

    # ------------------------------------------------------------------
    # Pause overlay
    # ------------------------------------------------------------------

    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        surface.blit(overlay, (0, 0))

        txt = self.font_title.render("PAUSED", True, WHITE)
        surface.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, 220))

        hint = self.font_small.render("Press  P  or  ESC  to Resume", True, (200, 200, 200))
        surface.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 310))

    # ------------------------------------------------------------------
    # Game-over overlay
    # ------------------------------------------------------------------

    def draw_gameover_overlay(self, surface, score, diff_cfg, new_record, score_mgr, chosen_difficulty):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        go = self.font_title.render("GAME OVER", True, RED)
        surface.blit(go, (WINDOW_WIDTH // 2 - go.get_width() // 2, 145))

        diff_lbl = diff_cfg.get("label", "")
        dt = self.font_small.render(f"Difficulty: {diff_lbl}", True, (200, 200, 200))
        surface.blit(dt, (WINDOW_WIDTH // 2 - dt.get_width() // 2, 220))

        st = self.font_large.render(f"Score: {score}", True, WHITE)
        surface.blit(st, (WINDOW_WIDTH // 2 - st.get_width() // 2, 260))

        best = score_mgr.get(chosen_difficulty)
        bc = YELLOW if new_record else (185, 185, 185)
        bt = self.font_medium.render(f"Best: {best}", True, bc)
        surface.blit(bt, (WINDOW_WIDTH // 2 - bt.get_width() // 2, 308))

        if new_record:
            nr = self.font_small.render("NEW RECORD!", True, YELLOW)
            surface.blit(nr, (WINDOW_WIDTH // 2 - nr.get_width() // 2, 348))

        rt = self.font_small.render("R  —  Retry (back to difficulty)", True, GREEN)
        qt = self.font_small.render("Q  —  Quit", True, RED)
        ay = 405 if new_record else 380
        surface.blit(rt, (WINDOW_WIDTH // 2 - rt.get_width() // 2, ay))
        surface.blit(qt, (WINDOW_WIDTH // 2 - qt.get_width() // 2, ay + 38))
