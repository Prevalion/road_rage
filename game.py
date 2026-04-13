import random
import pygame
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    BLACK, CYAN, WHITE,
    PLAYER_WIDTH, PLAYER_HEIGHT,
    STATE_MENU, STATE_DIFFICULTY, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    DIFFICULTIES,
)
from player import Player
from enemy import EnemyCar
from powerup import Powerup
from hud import HUD
from sounds import SoundManager, MUSIC_VOL_MENU, MUSIC_VOL_PLAYING
from road import Road, HighScoreManager
from ui import UIRenderer

# Difficulties that use smart (swerving) enemies
_SMART_DIFFICULTIES = {"Medium", "Hard"}


class Game:

    def __init__(self):
        pygame.init()

        # fullscreen
        flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((0, 0), flags)
        self.display_w = self.screen.get_width()
        self.display_h = self.screen.get_height()

        sx = self.display_w / WINDOW_WIDTH
        sy = self.display_h / WINDOW_HEIGHT
        self.render_scale = min(sx, sy)

        scaled_w = int(WINDOW_WIDTH * self.render_scale)
        scaled_h = int(WINDOW_HEIGHT * self.render_scale)
        self.render_offset_x = (self.display_w - scaled_w) // 2
        self.render_offset_y = (self.display_h - scaled_h) // 2

        self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.sound_mgr = SoundManager()
        self.score_mgr = HighScoreManager()
        self.ui = UIRenderer()
        self.sound_mgr.start_music(MUSIC_VOL_MENU)

        self.state = STATE_MENU

        # game objects (initialised per-round)
        self.road = None
        self.player_car = None
        self.all_sprites = None
        self.enemy_group = None
        self.powerup_group = None
        self.hud = None

        self.chosen_difficulty = "Easy"
        self.diff_cfg = {}
        self._hover_btn = None

        # gameplay counters
        self.score = 0
        self.lives = 0
        self.enemy_speed = 0.0
        self.spawn_rate = 0
        self._spawn_timer = 0
        self._speed_timer = 0
        self._heart_timer = 0
        self._shield_timer = 0
        self.new_record = False

        # menu road scroll
        self._menu_scroll = 0.0

    def _to_game_pos(self, screen_pos):
        rx, ry = screen_pos
        gx = (rx - self.render_offset_x) / self.render_scale
        gy = (ry - self.render_offset_y) / self.render_scale
        return (int(gx), int(gy))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
                return

            if self.state == STATE_MENU:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    self.state = STATE_DIFFICULTY

            elif self.state == STATE_DIFFICULTY:
                if ev.type == pygame.KEYDOWN:
                    pick = {pygame.K_1: "Easy", pygame.K_2: "Medium", pygame.K_3: "Hard"}.get(ev.key)
                    if pick:
                        self._start_round(pick)
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    click = self._to_game_pos(pygame.mouse.get_pos())
                    for dk, rect in self.ui.diff_buttons().items():
                        if rect.collidepoint(click):
                            self._start_round(dk)

            elif self.state == STATE_PLAYING:
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = STATE_PAUSED

            elif self.state == STATE_PAUSED:
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = STATE_PLAYING

            elif self.state == STATE_GAME_OVER:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        self.sound_mgr.set_music_volume(MUSIC_VOL_MENU)
                        self.state = STATE_DIFFICULTY
                    elif ev.key == pygame.K_q:
                        self.running = False

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self):
        if self.state == STATE_MENU:
            self._menu_scroll = (self._menu_scroll + 2.5) % UIRenderer._MENU_TILE_H

        elif self.state == STATE_DIFFICULTY:
            mpos = self._to_game_pos(pygame.mouse.get_pos())
            self._hover_btn = None
            for dk, rect in self.ui.diff_buttons().items():
                if rect.collidepoint(mpos):
                    self._hover_btn = dk
                    break

        elif self.state == STATE_PLAYING:
            self._tick_gameplay()

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        self.screen.fill(BLACK)
        canvas = self.game_surface
        canvas.fill(BLACK)

        if self.state == STATE_MENU:
            self.ui.draw_menu(canvas, self._menu_scroll)

        elif self.state == STATE_DIFFICULTY:
            self.ui.draw_difficulty(canvas, self._menu_scroll,
                                    self._hover_btn, self.score_mgr)

        elif self.state == STATE_PLAYING:
            self._draw_gameplay(canvas)

        elif self.state == STATE_PAUSED:
            self._draw_gameplay(canvas)
            self.ui.draw_pause_overlay(canvas)

        elif self.state == STATE_GAME_OVER:
            self._draw_gameplay(canvas)
            self.ui.draw_gameover_overlay(
                canvas, self.score, self.diff_cfg,
                self.new_record, self.score_mgr, self.chosen_difficulty,
            )

        # scale to fullscreen
        fw = int(WINDOW_WIDTH * self.render_scale)
        fh = int(WINDOW_HEIGHT * self.render_scale)
        scaled = pygame.transform.smoothscale(canvas, (fw, fh))
        self.screen.blit(scaled, (self.render_offset_x, self.render_offset_y))
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Round setup
    # ------------------------------------------------------------------

    def _start_round(self, diff_key):
        self.chosen_difficulty = diff_key
        self.diff_cfg = DIFFICULTIES[diff_key]
        cfg = self.diff_cfg

        self.road = Road(cfg["road_width"])
        left  = self.road.road_left
        right = self.road.road_right

        self.all_sprites   = pygame.sprite.Group()
        self.enemy_group   = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        self.player_car = Player(left, right)
        self.all_sprites.add(self.player_car)

        self.hud = HUD(cfg["lives"], cfg["label"])
        self.hud.high_score = self.score_mgr.get(diff_key)

        self.score       = 0
        self.lives       = cfg["lives"]
        self.enemy_speed = float(cfg["enemy_speed"])
        self.spawn_rate  = cfg["spawn_rate"]
        self._spawn_timer  = 0
        self._speed_timer  = 0
        self._heart_timer  = 0
        self._shield_timer = 0
        self.new_record    = False

        self.sound_mgr.set_music_volume(MUSIC_VOL_PLAYING)
        self.state = STATE_PLAYING

    # ------------------------------------------------------------------
    # Gameplay tick
    # ------------------------------------------------------------------

    def _tick_gameplay(self):
        cfg = self.diff_cfg
        self.score += 1

        # speed ramp
        self._speed_timer += 1
        bump_interval = cfg["speed_interval"] * FPS
        if self._speed_timer >= bump_interval:
            self.enemy_speed += cfg["speed_increment"]
            self.spawn_rate = max(20, self.spawn_rate - 4)
            self._speed_timer = 0

        # spawn enemies
        self._spawn_timer += 1
        variation  = int(self.spawn_rate * 0.2)
        min_wait   = max(10, self.spawn_rate - variation)
        max_wait   = self.spawn_rate + variation
        next_spawn = random.randint(min_wait, max_wait)

        if self._spawn_timer >= next_spawn:
            smart = self.chosen_difficulty in _SMART_DIFFICULTIES
            enemy = EnemyCar(
                self.road.road_left, self.road.road_right,
                self.enemy_speed, smart=smart,
            )
            self.enemy_group.add(enemy)
            self.all_sprites.add(enemy)
            self._spawn_timer = 0

        # powerups (easy mode only)
        if cfg.get("powerups"):
            self._tick_powerups(cfg)

        # scroll road
        self.road.update(max(3.0, self.enemy_speed))

        # update player
        pressed = pygame.key.get_pressed()
        self.player_car.update(pressed)

        # update enemies
        for e in list(self.enemy_group):
            e.update()
            if e.is_off_screen():
                e.kill()

        # update powerups
        for p in list(self.powerup_group):
            p.update()
            if p.is_off_screen():
                p.kill()

        # collisions
        self._check_collisions()
        self._check_pickups()

        # sync hud
        self.hud.update(
            self.lives, self.score,
            self.score_mgr.get(self.chosen_difficulty),
            self.player_car.shield_active,
            self.player_car.shield_timer,
        )

    def _tick_powerups(self, cfg):
        self._heart_timer  += 1
        self._shield_timer += 1

        if self._heart_timer >= cfg["heart_interval"] * FPS:
            h = Powerup("heart", self.road.road_left, self.road.road_right)
            self.powerup_group.add(h)
            self.all_sprites.add(h)
            self._heart_timer = 0

        if self._shield_timer >= cfg["shield_interval"] * FPS:
            s = Powerup("shield", self.road.road_left, self.road.road_right)
            self.powerup_group.add(s)
            self.all_sprites.add(s)
            self._shield_timer = 0

    def _check_collisions(self):
        hits = pygame.sprite.spritecollide(
            self.player_car, self.enemy_group, True, pygame.sprite.collide_rect)
        for _ in hits:
            if self.player_car.shield_active:
                self.player_car.block_hit_with_shield()
            else:
                self.player_car.take_hit()
                self.lives -= 1
                self.sound_mgr.play("collision")
                if self.lives <= 0:
                    self._end_game()
                    return

    def _check_pickups(self):
        collected = pygame.sprite.spritecollide(
            self.player_car, self.powerup_group, True, pygame.sprite.collide_rect)
        for item in collected:
            if item.powerup_type == "heart":
                self.sound_mgr.play("powerup")
                max_hp = self.diff_cfg["lives"]
                self.lives = min(max_hp, self.lives + 1)
            elif item.powerup_type == "shield":
                self.sound_mgr.play("shield")
                self.player_car.activate_shield()

    def _end_game(self):
        self.sound_mgr.set_music_volume(MUSIC_VOL_MENU)
        self.sound_mgr.play("game_over")
        self.new_record = self.score_mgr.update(self.chosen_difficulty, self.score)
        self.state = STATE_GAME_OVER

    # ------------------------------------------------------------------
    # Gameplay drawing
    # ------------------------------------------------------------------

    def _draw_gameplay(self, surface):
        self.road.draw(surface)
        self.all_sprites.draw(surface)

        # shield glow ring
        if self.player_car and self.player_car.shield_active:
            glow_r    = max(PLAYER_WIDTH, PLAYER_HEIGHT) // 2 + 10
            flash_thresh = 2 * 60
            nearly_done = self.player_car.shield_timer <= flash_thresh
            blink       = (self.player_car.shield_timer // 6) % 2 == 0
            ring_col    = WHITE if (nearly_done and blink) else CYAN
            pygame.draw.circle(surface, ring_col,
                               self.player_car.rect.center, glow_r, 3)

        self.hud.draw(surface)
