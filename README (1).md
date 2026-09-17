# 🚀 Space Wars

A 2D space shooter game developed using **Python and Pygame**. Control your spaceship, destroy enemy ships and asteroids, collect power-ups, and defeat the final boss to win the game.

## 🎮 About the Project

Space Wars is a simple arcade-style shooting game where the player controls a spaceship and fights against incoming enemies and obstacles.

The game features multiple difficulty levels, different enemy types, a scoring system, power-ups, and a boss battle that activates when the player reaches a score of 1000.

## ✨ Features

* **Three difficulty levels:** Easy, Medium, and Hard.
* **Player movement and shooting:** Move your spaceship and fire bullets at enemies.
* **Multiple enemy types:** Regular enemies, kamikaze enemies, and sine-wave-moving enemies.
* **Asteroid obstacles:** Destroy asteroids to earn points.
* **Power-ups:** Collect special items to improve your abilities.
* **Boss battle:** Fight a powerful boss after reaching 1000 points.
* **Lives and shields:** Protect your spaceship and survive enemy attacks.
* **Combo scoring:** Earn score multipliers by defeating enemies and destroying asteroids in succession.
* **Bomb ability:** Destroy regular enemies and asteroids on the screen.
* **Visual effects:** Enjoy explosions, particles, screen shake, and a scrolling starfield.
* **High-score tracking:** Save and display your highest score between game sessions.

## 🛠️ Technologies Used

| Technology | Purpose                                          |
| ---------- | ------------------------------------------------ |
| Python     | Game programming                                 |
| Pygame     | Graphics, sprites, keyboard input, and game loop |
| Random     | Random enemy behavior and power-up generation    |
| Math       | Enemy movement and particle effects              |
| OS         | High-score file handling                         |

## 📂 Project Structure

```text
Space-Wars/
│
├── space_wars.py
├── spaceship.png
├── enemy_spaceship.png
├── asteroid.png
├── bullet.png
├── highscore.txt
├── game_users.db
└── README.md
```

**Note:** The `game_users.db` SQLite database stores pilot profiles and high scores for the in-game Top 5 Pilots Hall of Fame. The overall top record is also mirrored in `highscore.txt`.

## ⚙️ Installation and Setup

### 1. Install Python

Download and install Python from the official website:

https://www.python.org/downloads/

### 2. Clone the repository

```bash
git clone https://github.com/sairaj-21/Spacewars.git
```



### 3. Navigate to the project directory

```bash
cd Space-Wars
```

### 4. Install Pygame

```bash
python -m pip install pygame
```

### 5. Run the game

```bash
python space_wars.py
```

The game window will open. Press the spacebar to start playing.

## 🕹️ Controls

| Key                      | Action                                     |
| ------------------------ | ------------------------------------------ |
| ↑ / W                    | Move spaceship up                          |
| ↓ / S                    | Move spaceship down                        |
| ← / A                    | Move spaceship left                        |
| → / D                    | Move spaceship right                       |
| Spacebar / Enter         | Shoot bullets / Confirm selection          |
| B                        | Use bomb (damages boss & clears screen)    |
| P / Escape               | Pause / Resume game                        |
| N (in menu)              | Change pilot callsign                      |
| L (in menu)              | View Top 5 Pilots Leaderboard              |

## ⚡ Power-Ups

Collect power-ups dropped by destroyed enemies and asteroids to gain special abilities.

| Power-Up       | Effect                                             |
| -------------- | -------------------------------------------------- |
| Shield         | Absorbs one hit                                    |
| Rapid Fire     | Increases shooting speed                           |
| Extra Life     | Adds one life, up to a maximum of 5                |
| Bomb           | Adds one bomb, up to a maximum of 3                |
| Spread Shot    | Fires multiple bullets in different directions     |
| Piercing Laser | Fires faster bullets that pass through enemies     |

Most temporary power-ups last for 5 seconds.

## 👾 Enemies and Boss Battle

### Enemy types

* **Regular Enemy:** Follows the player's vertical position and fires bullets.
* **Kamikaze Enemy:** Moves directly toward the player with homing vectors.
* **Sine Enemy:** Moves horizontally in a wave pattern while shooting.

### Boss Battle: Dreadnought M-1

When the score reaches **1000 points**, the boss battle begins with a warning klaxon.

The boss has 100 health points and uses two attack patterns:

1. Triple spread-shot attack.
2. Rapid-fire burst attack.

Defeat the boss to complete the game and display the victory screen.

## 🏆 Scoring System

| Action                                | Points |
| ------------------------------------- | -----: |
| Destroy an enemy                      |     50 |
| Destroy an asteroid                   |     15 |
| Defeat the boss                       |   1000 |

Combo multipliers increase the points earned from destroying enemies and asteroids, up to a maximum of 5×.

## 💾 High-Score & Leaderboard System

The game automatically tracks high scores across game sessions:

* **Real-Time HUD**: Displays the current session high score dynamically.
* **Database Leaderboard**: `game_users.db` saves high scores per pilot callsign with a dedicated Top 5 Hall of Fame screen.
* **Text Fallback**: Top overall score is mirrored to `highscore.txt`.



```markdown
![Main Menu](screenshots/main_menu.png)

![Gameplay](screenshots/gameplay.png)

![Boss Battle](screenshots/boss_battle.png)
```



## 👨‍💻 Author

**Sairaj Desai**

Developed as a personal Python game development project using Pygame.

## 📄 License

This project is available for learning and personal use. Add a license file to the repository if you want to specify the terms under which others can use, modify, or distribute the project.
