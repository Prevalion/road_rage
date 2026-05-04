import math
import array
import os
import pygame

# volume levels for bg music
MUSIC_VOL_MENU = 0.15
MUSIC_VOL_PLAYING = 0.40


class SoundManager:
    # sound name -> (filepath, fallback freq, fallback duration, volume)
    _SOUND_DEFS = {
        "collision": ("assets/sounds/hurt.mp3", 180, 140, 0.55),
        "powerup":  ("assets/sounds/heart.mp3", 880, 180, 0.45),
        "shield":   ("assets/sounds/shield.mp3", 660, 200, 0.50),
        "game_over": ("assets/sounds/gameover.mp3", 110, 700, 0.60),
    }

    _MUSIC_FILE = "assets/sounds/background.mp3"
    _BASE_FREQ = 44100

    def __init__(self):
        self._sounds = {}
        self._music_playing = False
        self._current_pitch = 1.0
        self._init_mixer()
        self._load_sounds()

    def _init_mixer(self, frequency=None):
        if frequency is None:
            frequency = self._BASE_FREQ
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=frequency, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"[SoundManager] mixer init failed: {e}")

    def _load_sounds(self):
        for name, (path, freq, dur, vol) in self._SOUND_DEFS.items():
            self._sounds[name] = self._load_one(path, freq, dur, vol)

    def _load_one(self, filepath, fallback_freq, fallback_dur, vol):
        if os.path.exists(filepath):
            try:
                snd = pygame.mixer.Sound(filepath)
                snd.set_volume(vol)
                return snd
            except pygame.error:
                pass
        # file missing, generate a tone
        return self._make_tone(fallback_freq, fallback_dur, vol)

    # --- music ---

    def start_music(self, volume=MUSIC_VOL_MENU):
        if self._music_playing:
            self.set_music_volume(volume)
            return
        if not os.path.exists(self._MUSIC_FILE):
            return
        try:
            pygame.mixer.music.load(self._MUSIC_FILE)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self._music_playing = True
        except pygame.error as e:
            print(f"[SoundManager] couldnt start music: {e}")

    def set_music_volume(self, vol):
        try:
            pygame.mixer.music.set_volume(vol)
        except pygame.error:
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self._music_playing = False
        except pygame.error:
            pass

    def set_pitch(self, pitch, volume=MUSIC_VOL_PLAYING):
        """Reinitialise the mixer at a scaled sample rate to shift pitch.

        Reloads all sound effects and restarts background music.
        """
        if pitch == self._current_pitch:
            return
        self._current_pitch = pitch
        new_freq = int(self._BASE_FREQ * pitch)
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=new_freq, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"[SoundManager] mixer reinit failed: {e}")
            return
        self._sounds.clear()
        self._load_sounds()
        self._music_playing = False
        self.start_music(volume)

    # --- tone generation fallback ---

    @staticmethod
    def _make_tone(freq, duration_ms, volume):
        try:
            if not pygame.mixer.get_init():
                return None

            sample_rate = 22050
            num_samples = int(sample_rate * duration_ms / 1000)
            omega = 2.0 * math.pi * freq

            vol_clamped = min(1.0, max(0.0, volume))
            amplitude = int(32767 * vol_clamped)

            # fade out at the end so it doesn't click
            fade_samples = min(int(sample_rate * 0.02), num_samples)

            buf = array.array("h")
            for i in range(num_samples):
                val = math.sin(omega * i / sample_rate)
                if i >= num_samples - fade_samples:
                    remaining = num_samples - i
                    val *= remaining / fade_samples
                buf.append(int(val * amplitude))

            snd = pygame.mixer.Sound(buffer=buf)
            snd.set_volume(volume)
            return snd
        except Exception as e:
            print(f"[SoundManager] tone generation failed: {e}")
            return None

    def play(self, sound_name):
        snd = self._sounds.get(sound_name)
        if snd is not None:
            try:
                snd.play()
            except pygame.error:
                pass
