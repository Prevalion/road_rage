# Road Rage 🚗💨

An infinite top-down car dodge game built with **Python 3.10+** and **Pygame**.
Dodge oncoming traffic for as long as you can — there is no finish line.

---

## Installation

1. Make sure **Python 3.10 or newer** is installed.
2. Install the only required third-party library:

```
pip install pygame
```

---

## How to Run

```
python main.py
```

The game renders at **800 × 600 px** and automatically scales to fit your screen if needed.

---

## Controls

| Key(s)          | Action                          |
|-----------------|----------------------------------|
| `←` / `A`       | Move car left                    |
| `→` / `D`       | Move car right                   |
| `↑` / `W`       | Move car forward (up)            |
| `↓` / `S`       | Move car backward (down)         |
| `ENTER`         | Confirm / start from menu        |
| `P` or `ESC`    | Pause / resume                   |
| `R`             | Retry (returns to difficulty select) |
| `Q`             | Quit the game                    |
| `1` / `2` / `3` | Select difficulty (keyboard shortcut) |

---

## Difficulty Levels

### Easy — Level 1
- Road width: **500 px** (widest)
- Starting enemy speed: **3 px/frame**, +0.5 every 15 seconds
- Enemy spawn rate: **1 every 90 frames** initially, decreasing over time
- Player lives: **3 hearts**
- **Powerups enabled:**
  - ❤ Heart — appears every ~10 s; restores 1 life (max 3)
  - 🛡 Shield — appears every ~15 s; grants 5 seconds of invincibility
    (HUD displays a countdown bar; bar flashes in the final 2 seconds)

### Medium — Level 2
- Road width: **380 px**
- Starting enemy speed: **5 px/frame**, +0.7 every 12 seconds
- Enemy spawn rate: **1 every 60 frames** initially
- Player lives: **3 hearts**
- No powerups

### Hard — Level 3
- Road width: **260 px** (narrowest)
- Starting enemy speed: **8 px/frame**, +1.0 every 8 seconds
- Enemy spawn rate: **1 every 40 frames** initially
- Player lives: **1 heart** — a single collision ends the game
- No powerups

---

## High Scores

Best scores per difficulty are saved automatically in `highscores.txt`
(plain text, one entry per line: `Easy:1500`).  
They are loaded on startup and displayed on both the HUD and the Game Over screen.

---

## Project Structure

```
road_rage/
├── main.py          # Entry point
├── game.py          # Game controller, Road, HighScoreManager, state machine
├── player.py        # Player sprite
├── enemy.py         # EnemyCar sprite
├── powerup.py       # Powerup sprite (Easy mode)
├── hud.py           # HUD overlay
├── sounds.py        # SoundManager (loads files or synthesises tones)
├── constants.py     # Shared constants and difficulty configs
├── highscores.txt   # Persisted best scores
├── assets/
│   ├── sounds/      # Optional .wav/.ogg files (generated if absent)
│   └── images/      # Optional car sprites (programmatic fallback used)
└── README.md
```

---

## Assets

All graphics are drawn programmatically with `pygame.draw` — no image files required.  
All sounds are synthesised from pure Python (`math` + `array`) if no `.wav` files
are found in `assets/sounds/`.  
The game works **out of the box** even if the `assets/` folder is empty.
