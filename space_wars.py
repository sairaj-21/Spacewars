import pygame
import random
import os
import math
import sqlite3
import array

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 45)
LIGHT_GRAY = (180, 180, 180)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (50, 255, 50)
PURPLE = (180, 50, 255)
ORANGE = (255, 150, 0)
GOLD = (255, 215, 0)
SILVER = (200, 200, 220)
BRONZE = (205, 127, 50)
FPS = 60

# Screen setup
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Wars')
clock = pygame.time.Clock()

# ----------------------------------------------------
# 1. OPTIMIZED FONT CACHE
# ----------------------------------------------------
_FONT_CACHE = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = pygame.font.SysFont("arial" if pygame.font.match_font("arial") else None, size, bold=bold)
        except Exception:
            _FONT_CACHE[key] = pygame.font.SysFont(None, size, bold=bold)
    return _FONT_CACHE[key]

def display_text(text, size, color, x, y, surface=window, bold=False, align="center"):
    font = get_font(size, bold=bold)
    rendered_text = font.render(str(text), True, color)
    if align == "center":
        text_rect = rendered_text.get_rect(center=(int(x), int(y)))
    elif align == "left":
        text_rect = rendered_text.get_rect(midleft=(int(x), int(y)))
    elif align == "right":
        text_rect = rendered_text.get_rect(midright=(int(x), int(y)))
    else:
        text_rect = rendered_text.get_rect(center=(int(x), int(y)))
    surface.blit(rendered_text, text_rect)

# ----------------------------------------------------
# 2. PROCEDURAL RETRO AUDIO ENGINE (ZERO EXTERNAL FILES)
# ----------------------------------------------------
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            print(f"Audio notice: {e}. Running in silent mode.")
            self.enabled = False

    def _generate_sounds(self):
        try:
            self.sounds['laser'] = self._make_laser()
            self.sounds['explosion'] = self._make_noise(duration=0.22, decay=6.0, volume=0.45)
            self.sounds['bomb'] = self._make_bomb()
            self.sounds['powerup'] = self._make_arpeggio([523, 659, 784, 1046], duration=0.22)
            self.sounds['hurt'] = self._make_hurt()
            self.sounds['alarm'] = self._make_alarm()
        except Exception as e:
            print(f"Sound generation warning: {e}")
            self.enabled = False

    def _make_laser(self):
        sample_rate = 22050
        duration = 0.11
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            freq = 950.0 * (1.0 - t) + 260.0 * t
            phase += 2.0 * math.pi * freq / sample_rate
            env = 1.0 - t
            val = int(14000 * math.sin(phase) * env)
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def _make_noise(self, duration=0.22, decay=6.0, volume=0.45):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n_samples):
            t = i / n_samples
            env = math.exp(-decay * t)
            noise = (random.random() * 2.0 - 1.0)
            val = int(32767 * volume * noise * env)
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def _make_bomb(self):
        sample_rate = 22050
        duration = 0.55
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            freq = 75.0 * (1.0 - t * 0.5)
            phase += 2.0 * math.pi * freq / sample_rate
            env = math.exp(-3.5 * t)
            noise = (random.random() * 2.0 - 1.0) * 0.35
            wave = (math.sin(phase) * 0.65 + noise)
            val = int(25000 * wave * env)
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def _make_arpeggio(self, freqs, duration=0.22):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        step = max(1, n_samples // len(freqs))
        buf = array.array('h')
        phase = 0.0
        for i in range(n_samples):
            note_idx = min(i // step, len(freqs) - 1)
            freq = freqs[note_idx]
            phase += 2.0 * math.pi * freq / sample_rate
            note_pos = (i % step) / step
            env = (1.0 - note_pos * 0.25)
            val = int(14000 * math.sin(phase) * env)
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def _make_hurt(self):
        sample_rate = 22050
        duration = 0.14
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            freq = 140.0 * (1.0 - t * 0.45)
            phase += 2.0 * math.pi * freq / sample_rate
            val = int(18000 * (1.0 if math.sin(phase) > 0 else -1.0) * (1.0 - t))
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def _make_alarm(self):
        sample_rate = 22050
        duration = 0.35
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        phase = 0.0
        chunk = sample_rate // 10
        for i in range(n_samples):
            freq = 600.0 if (i // chunk) % 2 == 0 else 460.0
            phase += 2.0 * math.pi * freq / sample_rate
            val = int(12000 * (1.0 if math.sin(phase) > 0 else -1.0))
            buf.append(max(-32768, min(32767, val)))
        return pygame.mixer.Sound(buffer=buf)

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

sound_manager = SoundManager()

# ----------------------------------------------------
# 3. DATABASE & HIGH SCORE INTEGRATION
# ----------------------------------------------------
DB_FILE = "game_users.db"
TXT_FILE = "highscore.txt"

def init_database():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT DEFAULT '',
                high_score INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database init warning: {e}")

init_database()

def load_high_score():
    score = 0
    if os.path.exists(TXT_FILE):
        try:
            with open(TXT_FILE, "r") as f:
                score = int(f.read().strip())
        except Exception:
            score = 0
    return score

def save_high_score(score):
    try:
        with open(TXT_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

def get_pilot_best(username):
    if not username: return 0
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
    except Exception:
        return 0

def save_pilot_score(username, score):
    username = (username.strip() or "Ace Pilot")[:14]
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, high_score)
            VALUES (?, '', ?)
            ON CONFLICT(username) DO UPDATE SET high_score = MAX(users.high_score, excluded.high_score)
        """, (username, score))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving to database: {e}")

def get_top_pilots(limit=5):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, high_score FROM users ORDER BY high_score DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

# Load images safely
def load_image(name, size):
    try:
        image = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error:
        print(f"Warning: Could not load {name}, using fallback block.")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if "bullet" in name: surf.fill(YELLOW)
        elif "asteroid" in name: surf.fill((150, 75, 0))
        elif "enemy" in name: surf.fill(RED)
        else: surf.fill(GREEN)
        return surf

player_image = load_image("spaceship.png", (50, 30))
enemy_image = load_image("enemy_spaceship.png", (50, 30))
asteroid_image = load_image("asteroid.png", (30, 30))
bullet_image = load_image("bullet.png", (10, 10))
mini_player_img = pygame.transform.scale(player_image, (25, 15))

# Boss Image Fallback
try:
    boss_image = pygame.image.load("enemy_spaceship.png").convert_alpha()
    boss_image = pygame.transform.scale(boss_image, (150, 100))
except pygame.error:
    boss_image = pygame.Surface((150, 100), pygame.SRCALPHA)
    boss_image.fill(PURPLE)

# --- SPRITE CLASSES ---

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color=YELLOW, size=24):
        super().__init__()
        font = get_font(size, bold=True)
        self.image_orig = font.render(str(text), True, color)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.lifetime = 45
        self.max_lifetime = 45

    def update(self):
        self.rect.y -= 1
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        elif self.lifetime < 15:
            alpha = int(255 * (self.lifetime / 15))
            self.image = self.image_orig.copy()
            self.image.set_alpha(max(0, alpha))

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(15, 30)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

def create_explosion(x, y, color, count, all_sprites, particles):
    for _ in range(count):
        p = Particle(x, y, color)
        all_sprites.add(p)
        particles.add(p)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['shield', 'rapid_fire', 'life', 'bomb', 'spread_shot', 'piercing_laser'])
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        color_map = {
            'shield': CYAN,
            'rapid_fire': YELLOW,
            'bomb': WHITE,
            'spread_shot': ORANGE,
            'piercing_laser': PURPLE,
            'life': RED
        }
        color = color_map.get(self.type, RED)
        pygame.draw.circle(self.image, color, (11, 11), 10)
        pygame.draw.circle(self.image, WHITE, (11, 11), 5)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = -3
        self.speed_y = random.choice([-1, 0, 1])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_original = player_image
        self.image = self.image_original
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT // 2)
        self.speed = 6
        self.shoot_delay = 15
        self.last_shot = 0
        
        self.lives = 3
        self.invulnerable_timer = 0
        self.has_shield = False
        self.rapid_fire_timer = 0
        self.spread_shot_timer = 0
        self.piercing_laser_timer = 0
        self.bombs = 1
        self.boss_mode_active = False

    def update_state(self, keys):
        dx, dy = 0, 0
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            dy -= 1
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < HEIGHT:
            dy += 1
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            dx -= 1
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH // 2:
            dx += 1
            
        # Normalized diagonal movement
        if dx != 0 and dy != 0:
            self.rect.x += int(dx * self.speed * 0.7071)
            self.rect.y += int(dy * self.speed * 0.7071)
        else:
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        # Boundary clamping
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH // 2: self.rect.right = WIDTH // 2
        
        self.last_shot += 1

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        if self.spread_shot_timer > 0:
            self.spread_shot_timer -= 1
        if self.piercing_laser_timer > 0:
            self.piercing_laser_timer -= 1
            
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer % 10 < 5:
                self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
            else:
                self.image = self.image_original
        else:
            self.image = self.image_original

    def shoot(self, all_sprites, bullets):
        delay = 5 if self.rapid_fire_timer > 0 else self.shoot_delay
        if self.last_shot >= delay:
            is_piercing = self.piercing_laser_timer > 0
            bullet_speed = 15 if is_piercing else 10
            
            if self.boss_mode_active or self.spread_shot_timer > 0:
                for vy in [-2, 0, 2]:
                    bullet = Bullet(self.rect.right, self.rect.centery, bullet_speed, piercing=is_piercing)
                    bullet.speed_y = vy
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            else:
                bullet = Bullet(self.rect.right, self.rect.centery, bullet_speed, piercing=is_piercing)
                all_sprites.add(bullet)
                bullets.add(bullet)
                
            sound_manager.play('laser')
            self.last_shot = 0
            
    def take_damage(self):
        if self.invulnerable_timer == 0:
            if self.has_shield:
                self.has_shield = False
                self.invulnerable_timer = 60
            else:
                self.lives -= 1
                self.invulnerable_timer = 90
            sound_manager.play('hurt')
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed, shoot_cooldown):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH - 100, HEIGHT // 2)
        self.speed = speed
        self.shoot_cooldown = shoot_cooldown
        self.last_shot = 0

    def update_state(self, player_x, player_y, all_sprites, enemy_bullets):
        if self.rect.centery < player_y:
            self.rect.y += self.speed
        elif self.rect.centery > player_y:
            self.rect.y -= self.speed
        
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

        self.last_shot += 1
        if self.last_shot >= self.shoot_cooldown:
            bullet = Bullet(self.rect.left, self.rect.centery, -10)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.last_shot = 0

class Kamikaze(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.transform.scale(enemy_image, (40, 25))
        self.image.fill((255, 100, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + 50, random.randint(50, HEIGHT - 50))
        self.speed = speed * 1.2

    def update_state(self, player_x, player_y, all_sprites, enemy_bullets):
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

class SineEnemy(pygame.sprite.Sprite):
    def __init__(self, speed, shoot_cooldown):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + 50, random.randint(100, HEIGHT - 100))
        self.speed = speed
        self.shoot_cooldown = shoot_cooldown
        self.last_shot = 0
        self.start_y = self.rect.y
        self.time = 0

    def update_state(self, player_x, player_y, all_sprites, enemy_bullets):
        self.rect.x -= self.speed
        self.time += 0.05
        self.rect.y = self.start_y + math.sin(self.time) * 150
        
        self.last_shot += 1
        if self.last_shot >= self.shoot_cooldown:
            bullet = Bullet(self.rect.left, self.rect.centery, -8)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.last_shot = 0

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + 200, HEIGHT // 2) # Start offscreen
        self.health = 100
        self.max_health = 100
        self.speed_y = 3
        self.shoot_cooldown = 40
        self.last_shot = 0
        self.state = 'entering' # entering, fighting
        self.attack_pattern = 0
        self.attack_timer = 0

    def update_state(self, player_y, all_sprites, enemy_bullets):
        if self.state == 'entering':
            self.rect.x -= 2
            if self.rect.right <= WIDTH - 20:
                self.state = 'fighting'
        elif self.state == 'fighting':
            # Complex Movement (Oscillate)
            self.rect.y += self.speed_y
            if self.rect.bottom > HEIGHT - 50 or self.rect.top < 50:
                self.speed_y *= -1

            # Attack Logic
            self.last_shot += 1
            self.attack_timer += 1
            
            # Switch attack patterns every 5 seconds
            if self.attack_timer > 300:
                self.attack_timer = 0
                self.attack_pattern = (self.attack_pattern + 1) % 2
                
            if self.attack_pattern == 0:
                # Standard triple spread shot
                if self.last_shot >= self.shoot_cooldown:
                    for vy in [-2, 0, 2]:
                        bullet = Bullet(self.rect.left, self.rect.centery, -8)
                        bullet.speed_y = vy  # Modify Bullet class to support speed_y
                        all_sprites.add(bullet)
                        enemy_bullets.add(bullet)
                    self.last_shot = 0
            elif self.attack_pattern == 1:
                # Rapid fire burst
                if self.last_shot >= 15:
                    bullet = Bullet(self.rect.left, self.rect.centery + random.randint(-40, 40), -12)
                    all_sprites.add(bullet)
                    enemy_bullets.add(bullet)
                    self.last_shot = 0

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = asteroid_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH + 20, WIDTH + 200)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, piercing=False):
        super().__init__()
        self.piercing = piercing
        if self.piercing:
            self.image = pygame.Surface((16, 6))
            self.image.fill(PURPLE)
            pygame.draw.rect(self.image, WHITE, (2, 2, 12, 2))
        else:
            self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = speed_x
        self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# --- GAME SCREENS ---

def pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    window.blit(overlay, (0, 0))
    
    display_text("GAME PAUSED", 60, YELLOW, WIDTH // 2, HEIGHT // 2 - 60, bold=True)
    display_text("Press P or ESC to Resume", 30, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
    display_text("Press Q to Quit to Menu", 25, RED, WIDTH // 2, HEIGHT // 2 + 60)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    return False  # Continue playing
                if event.key == pygame.K_q:
                    return True   # Quit to menu
        clock.tick(30)

def leaderboard_screen():
    pilots = get_top_pilots(5)
    running = True
    
    while running:
        window.fill(BLACK)
        display_text("TOP PILOTS HALL OF FAME", 46, GOLD, WIDTH // 2, 80, bold=True)
        display_text("Rankings stored in database", 20, GRAY, WIDTH // 2, 125)
        
        y_start = 180
        if not pilots:
            display_text("No pilot records found yet. Go fly and make history!", 28, LIGHT_GRAY, WIDTH // 2, 260)
        else:
            rank_colors = [GOLD, SILVER, BRONZE, WHITE, WHITE]
            for i, (name, high_score) in enumerate(pilots):
                color = rank_colors[i] if i < len(rank_colors) else WHITE
                rank_str = f"#{i+1}"
                
                # Draw card row
                card_rect = pygame.Rect(WIDTH // 2 - 250, y_start + i * 55, 500, 44)
                pygame.draw.rect(window, DARK_GRAY, card_rect, border_radius=8)
                pygame.draw.rect(window, color, card_rect, width=2, border_radius=8)
                
                display_text(rank_str, 28, color, card_rect.left + 40, card_rect.centery, bold=True)
                display_text(name, 26, WHITE, card_rect.left + 120, card_rect.centery, align="left")
                display_text(f"{high_score:,} pts", 26, YELLOW, card_rect.right - 30, card_rect.centery, align="right")

        back_btn = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 85, 180, 45)
        pygame.draw.rect(window, GRAY, back_btn, border_radius=8)
        display_text("Back [ESC]", 24, WHITE, back_btn.centerx, back_btn.centery)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    running = False
        clock.tick(30)

def name_input_screen(current_name):
    name = current_name
    input_box = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 25, 320, 50)
    running = True
    
    while running:
        window.fill(BLACK)
        display_text("ENTER PILOT CALLSIGN", 44, CYAN, WIDTH // 2, HEIGHT // 2 - 100, bold=True)
        display_text("Type your name and press ENTER", 22, GRAY, WIDTH // 2, HEIGHT // 2 - 50)
        
        pygame.draw.rect(window, DARK_GRAY, input_box, border_radius=8)
        pygame.draw.rect(window, CYAN, input_box, width=3, border_radius=8)
        display_text(name if name else "...", 32, WHITE if name else GRAY, input_box.centerx, input_box.centery)
        
        confirm_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 45)
        pygame.draw.rect(window, GRAY, confirm_btn, border_radius=8)
        display_text("Confirm", 24, WHITE, confirm_btn.centerx, confirm_btn.centery)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() or "Ace Pilot"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if confirm_btn.collidepoint(event.pos):
                    return name.strip() or "Ace Pilot"
        clock.tick(30)

def difficulty_selection_screen():
    window.fill(BLACK)
    display_text("Select Difficulty", 55, WHITE, WIDTH // 2, HEIGHT // 2 - 110, bold=True)

    easy_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 40, 240, 50)
    medium_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 30, 240, 50)
    hard_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 100, 240, 50)

    pygame.draw.rect(window, (40, 140, 40), easy_button, border_radius=10)
    pygame.draw.rect(window, (160, 140, 30), medium_button, border_radius=10)
    pygame.draw.rect(window, (160, 40, 40), hard_button, border_radius=10)
    
    display_text("Easy (Casual)", 28, WHITE, easy_button.centerx, easy_button.centery)
    display_text("Medium (Standard)", 28, WHITE, medium_button.centerx, medium_button.centery)
    display_text("Hard (Intense)", 28, WHITE, hard_button.centerx, hard_button.centery)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos): return "Easy"
                elif medium_button.collidepoint(event.pos): return "Medium"
                elif hard_button.collidepoint(event.pos): return "Hard"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: return "Easy"
                elif event.key == pygame.K_2: return "Medium"
                elif event.key == pygame.K_3: return "Hard"
                elif event.key == pygame.K_ESCAPE: return "Medium"

def game_over_screen(score, high_score, won=False, pilot_name="Ace Pilot"):
    window.fill(BLACK)
    if won:
        display_text("MISSION ACCOMPLISHED!", 62, GREEN, WIDTH // 2, HEIGHT // 2 - 110, bold=True)
        display_text("You eliminated the Boss and saved the sector!", 26, WHITE, WIDTH // 2, HEIGHT // 2 - 60)
    else:
        display_text("SYSTEM FAILURE", 65, RED, WIDTH // 2, HEIGHT // 2 - 110, bold=True)
        display_text("Your spaceship was destroyed in combat.", 24, GRAY, WIDTH // 2, HEIGHT // 2 - 60)
        
    display_text(f"Pilot: {pilot_name}", 32, CYAN, WIDTH // 2, HEIGHT // 2 - 15)
    display_text(f"Final Score: {score:,}", 38, WHITE, WIDTH // 2, HEIGHT // 2 + 25)
    display_text(f"High Score: {high_score:,}", 32, YELLOW, WIDTH // 2, HEIGHT // 2 + 65)

    restart_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 120, 220, 50)
    pygame.draw.rect(window, GRAY, restart_button, border_radius=10)
    display_text("Play Again", 28, WHITE, restart_button.centerx, restart_button.centery)
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                    return

# --- MAIN GAME LOOP ---

def game_loop(difficulty, pilot_name="Ace Pilot"):
    if difficulty == "Easy":
        ast_spd, comp_spd, comp_cd, max_asteroids = 4, 3, 60, 4
    elif difficulty == "Medium":
        ast_spd, comp_spd, comp_cd, max_asteroids = 6, 4, 40, 6
    else:
        ast_spd, comp_spd, comp_cd, max_asteroids = 8, 5, 25, 8

    all_sprites = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    floating_texts = pygame.sprite.Group()

    for _ in range(50):
        star = Star()
        all_sprites.add(star)
        stars.add(star)

    player = Player()
    enemy = Enemy(comp_spd, comp_cd)
    all_sprites.add(player, enemy)
    enemies.add(enemy)
    
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    shake_timer = 0
    bomb_flash_timer = 0
    boss_warning_timer = 0
    
    combo = 0
    combo_timer = 0
    score_multiplier = 1

    for _ in range(max_asteroids):
        asteroid = Asteroid(ast_spd)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    score = 0
    saved_high = max(load_high_score(), get_pilot_best(pilot_name))
    running = True
    boss_active = False
    boss = None
    won = False
    
    BOSS_THRESHOLD = 1000
    
    def spawn_powerup(x, y):
        if random.random() < 0.18:
            pu = PowerUp(x, y)
            all_sprites.add(pu)
            powerups.add(pu)

    while running:
        game_surface.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Pause Support
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    should_quit = pause_menu()
                    if should_quit:
                        return
                        
                # Bomb Support (Normal waves + Boss battle)
                if event.key == pygame.K_b and player.bombs > 0:
                    player.bombs -= 1
                    bomb_flash_timer = 12
                    shake_timer = 30
                    sound_manager.play('bomb')
                    
                    if boss_active and boss and boss.state == 'fighting':
                        boss.health -= 15
                        create_explosion(boss.rect.centerx, boss.rect.centery, PURPLE, 40, all_sprites, particles)
                        txt = FloatingText("-15 BOMB DAMAGE!", boss.rect.centerx, boss.rect.centery - 30, RED, 26)
                        all_sprites.add(txt)
                        floating_texts.add(txt)
                        # Clear all enemy bullets on screen
                        for b in list(enemy_bullets):
                            create_explosion(b.rect.centerx, b.rect.centery, YELLOW, 4, all_sprites, particles)
                            b.kill()
                        if boss.health <= 0:
                            score += 1000
                            create_explosion(boss.rect.centerx, boss.rect.centery, PURPLE, 100, all_sprites, particles)
                            boss.kill()
                            shake_timer = 60
                            won = True
                            running = False
                    else:
                        for e in list(enemies):
                            create_explosion(e.rect.centerx, e.rect.centery, RED, 20, all_sprites, particles)
                            pts = 50 * score_multiplier
                            score += pts
                            combo += 1
                            txt = FloatingText(f"+{pts}", e.rect.centerx, e.rect.centery, YELLOW)
                            all_sprites.add(txt)
                            floating_texts.add(txt)
                            e.kill()
                        for ast in list(asteroids):
                            create_explosion(ast.rect.centerx, ast.rect.centery, GRAY, 10, all_sprites, particles)
                            pts = 15 * score_multiplier
                            score += pts
                            combo += 1
                            txt = FloatingText(f"+{pts}", ast.rect.centerx, ast.rect.centery, WHITE)
                            all_sprites.add(txt)
                            floating_texts.add(txt)
                            ast.kill()
                        combo_timer = 180

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot(all_sprites, player_bullets)
            
        # Engine particles
        if (keys[pygame.K_UP] or keys[pygame.K_w] or 
            keys[pygame.K_DOWN] or keys[pygame.K_s] or 
            keys[pygame.K_LEFT] or keys[pygame.K_a] or 
            keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            p = Particle(player.rect.left + 5, player.rect.centery + random.randint(-5, 5), (255, random.randint(120, 220), 0))
            p.vx = -random.uniform(3, 6)
            p.vy = random.uniform(-1, 1)
            all_sprites.add(p)
            particles.add(p)

        # Triggers Boss Phase
        if score >= BOSS_THRESHOLD and not boss_active:
            boss_active = True
            boss = Boss()
            all_sprites.add(boss)
            boss_warning_timer = 160
            sound_manager.play('alarm')
            
            spawn_powerup((WIDTH // 2) + 100, HEIGHT // 2)
            guaranteed_pu = PowerUp((WIDTH // 2) + 100, HEIGHT // 2)
            all_sprites.add(guaranteed_pu)
            powerups.add(guaranteed_pu)
            
            player.boss_mode_active = True
            player.lives = max(player.lives, 3)
            
            for e in list(enemies):
                create_explosion(e.rect.centerx, e.rect.centery, RED, 15, all_sprites, particles)
                e.kill()
            for ast in list(asteroids):
                create_explosion(ast.rect.centerx, ast.rect.centery, GRAY, 10, all_sprites, particles)
                ast.kill()

        if combo_timer > 0:
            combo_timer -= 1
            if combo_timer == 0:
                combo = 0
                score_multiplier = 1
        else:
            score_multiplier = min(5, 1 + (combo // 5))

        # Updates
        stars.update()
        player_bullets.update()
        enemy_bullets.update()
        powerups.update()
        particles.update()
        floating_texts.update()
        player.update_state(keys)

        if boss_active and boss:
            boss.update_state(player.rect.centery, all_sprites, enemy_bullets)
        else:
            asteroids.update()
            for e in enemies:
                e.update_state(player.rect.centerx, player.rect.centery, all_sprites, enemy_bullets)

        # Mechanics When Boss Is NOT Active
        if not boss_active:
            # Evasion off-screen awards 0 pts
            for asteroid in list(asteroids):
                if asteroid.rect.right < 0:
                    asteroid.kill()
            
            for e in list(enemies):
                if e.rect.right < 0:
                    e.kill()
            
            # Player bullets hit enemies
            for e in list(enemies):
                hit_bullets = pygame.sprite.spritecollide(e, player_bullets, False)
                if hit_bullets:
                    for b in hit_bullets:
                        if not b.piercing:
                            b.kill()
                    pts = 50 * score_multiplier
                    score += pts
                    combo += 1
                    combo_timer = 180
                    score_multiplier = min(5, 1 + (combo // 5))
                    create_explosion(e.rect.centerx, e.rect.centery, RED, 20, all_sprites, particles)
                    sound_manager.play('explosion')
                    txt = FloatingText(f"+{pts}", e.rect.centerx, e.rect.centery, YELLOW)
                    all_sprites.add(txt)
                    floating_texts.add(txt)
                    spawn_powerup(e.rect.centerx, e.rect.centery)
                    e.kill()
                
            # Maintain enemies
            target_enemy_count = 2 if score > 150 else 1
            if len(enemies) < target_enemy_count:
                choice = random.choice([0, 1, 2])
                if choice == 0: new_e = Enemy(comp_spd, comp_cd)
                elif choice == 1: new_e = Kamikaze(comp_spd)
                else: new_e = SineEnemy(comp_spd, comp_cd)
                all_sprites.add(new_e)
                enemies.add(new_e)

            # Player bullets hit asteroids
            for ast in list(asteroids):
                hit_bullets = pygame.sprite.spritecollide(ast, player_bullets, False)
                if hit_bullets:
                    for b in hit_bullets:
                        if not b.piercing:
                            b.kill()
                    pts = 15 * score_multiplier
                    score += pts
                    combo += 1
                    combo_timer = 180
                    score_multiplier = min(5, 1 + (combo // 5))
                    create_explosion(ast.rect.centerx, ast.rect.centery, GRAY, 10, all_sprites, particles)
                    sound_manager.play('explosion')
                    txt = FloatingText(f"+{pts}", ast.rect.centerx, ast.rect.centery, WHITE)
                    all_sprites.add(txt)
                    floating_texts.add(txt)
                    spawn_powerup(ast.rect.centerx, ast.rect.centery)
                    ast.kill()
            
            # Maintain asteroid count
            while len(asteroids) < max_asteroids:
                new_asteroid = Asteroid(ast_spd)
                all_sprites.add(new_asteroid)
                asteroids.add(new_asteroid)

        # Mechanics When Boss IS Active
        if boss_active and boss and boss.state == 'fighting':
            hit_bullets = pygame.sprite.spritecollide(boss, player_bullets, False)
            if hit_bullets:
                damage_dealt = 0
                for b in hit_bullets:
                    damage_dealt += 1
                    if not b.piercing:
                        b.kill()
                boss.health -= damage_dealt
                create_explosion(boss.rect.left + 15, player.rect.centery, (255, 180, 0), 4, all_sprites, particles)
                sound_manager.play('hurt')
                
                if boss.health <= 0:
                    score += 1000
                    create_explosion(boss.rect.centerx, boss.rect.centery, PURPLE, 100, all_sprites, particles)
                    txt = FloatingText("+1000 BOSS DEFEATED!", boss.rect.centerx, boss.rect.centery - 30, GOLD, 30)
                    all_sprites.add(txt)
                    floating_texts.add(txt)
                    boss.kill()
                    shake_timer = 60
                    won = True
                    running = False

        # Collect Powerups
        collected = pygame.sprite.spritecollide(player, powerups, True)
        for pu in collected:
            sound_manager.play('powerup')
            label = ""
            if pu.type == 'shield':
                player.has_shield = True
                label = "SHIELD ACTIVE!"
            elif pu.type == 'rapid_fire':
                player.rapid_fire_timer = 300
                label = "RAPID FIRE!"
            elif pu.type == 'life':
                player.lives = min(player.lives + 1, 5)
                label = "+1 EXTRA LIFE!"
            elif pu.type == 'bomb':
                player.bombs = min(player.bombs + 1, 3)
                label = "+1 BOMB!"
            elif pu.type == 'spread_shot':
                player.spread_shot_timer = 300
                label = "SPREAD SHOT!"
            elif pu.type == 'piercing_laser':
                player.piercing_laser_timer = 300
                label = "PIERCING LASER!"
            if label:
                txt = FloatingText(label, player.rect.centerx, player.rect.top - 15, CYAN, 22)
                all_sprites.add(txt)
                floating_texts.add(txt)

        # Take Damage
        hit_by_enemy_bullets = pygame.sprite.spritecollide(player, enemy_bullets, True)
        hit_by_asteroids = pygame.sprite.spritecollide(player, asteroids, False)
        hit_by_enemy = True if not boss_active and pygame.sprite.spritecollide(player, enemies, False) else False
        hit_by_boss = pygame.sprite.collide_rect(player, boss) if boss_active and boss else False

        if hit_by_enemy_bullets or hit_by_asteroids or hit_by_enemy or hit_by_boss:
            if player.take_damage():
                create_explosion(player.rect.centerx, player.rect.centery, YELLOW, 15, all_sprites, particles)
                shake_timer = 20
                
            if player.lives <= 0:
                running = False

        # Draw to game_surface
        all_sprites.draw(game_surface)
        
        # Draw Shield Visual
        if player.has_shield:
            pygame.draw.circle(game_surface, CYAN, player.rect.center, 30, 2)

        # Apply Screen Shake
        shake_offset_x = random.randint(-8, 8) if shake_timer > 0 else 0
        shake_offset_y = random.randint(-8, 8) if shake_timer > 0 else 0
        if shake_timer > 0:
            shake_timer -= 1
            
        window.fill(BLACK)
        window.blit(game_surface, (shake_offset_x, shake_offset_y))

        # Apply Bomb Flash effect
        if bomb_flash_timer > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            alpha = int(255 * (bomb_flash_timer / 12))
            flash_surface.set_alpha(alpha)
            flash_surface.fill(WHITE)
            window.blit(flash_surface, (0, 0))
            bomb_flash_timer -= 1

        # Boss Incoming Warning Banner
        if boss_warning_timer > 0:
            boss_warning_timer -= 1
            if (boss_warning_timer // 15) % 2 == 0:
                banner_rect = pygame.Rect(0, HEIGHT // 2 - 40, WIDTH, 80)
                banner_surf = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
                banner_surf.fill((200, 0, 0, 180))
                window.blit(banner_surf, (0, HEIGHT // 2 - 40))
                pygame.draw.rect(window, YELLOW, banner_rect, 3)
                display_text("WARNING: BOSS APPROACHING!", 42, WHITE, WIDTH // 2, HEIGHT // 2, bold=True)

        # Draw Boss Health Bar HUD
        if boss_active and boss and boss.state == 'fighting':
            bar_width = 420
            bar_height = 20
            health_ratio = max(0, boss.health / boss.max_health)
            bar_x = WIDTH // 2 - bar_width // 2
            pygame.draw.rect(window, DARK_GRAY, (bar_x, 25, bar_width, bar_height), border_radius=5)
            pygame.draw.rect(window, RED, (bar_x, 25, int(bar_width * health_ratio), bar_height), border_radius=5)
            pygame.draw.rect(window, WHITE, (bar_x, 25, bar_width, bar_height), 2, border_radius=5)
            display_text(f"DREADNOUGHT M-1  ({max(0, boss.health)} / {boss.max_health} HP)", 20, WHITE, WIDTH // 2, 14, bold=True)

        # Dynamic Real-time HUD
        live_high = max(score, saved_high)
        display_text(f"Score: {score:,}", 28, WHITE, 85, 22, align="left")
        display_text(f"High: {live_high:,}", 26, YELLOW, WIDTH - 20, 22, align="right")
        
        # Display Lives
        display_text("Lives:", 24, WHITE, WIDTH // 2 - 40, HEIGHT - 20)
        for i in range(player.lives):
            window.blit(mini_player_img, (WIDTH // 2 + 5 + i * 28, HEIGHT - 28))
            
        # Display Bombs
        bomb_color = WHITE if player.bombs > 0 else GRAY
        display_text(f"Bombs [B]: {player.bombs}", 24, bomb_color, 90, HEIGHT - 20, align="left")
            
        # UI for Active Power-ups
        status_y = 55
        if player.rapid_fire_timer > 0:
            display_text(f"Rapid Fire: {player.rapid_fire_timer // 60}s", 22, YELLOW, 85, status_y, align="left")
            status_y += 24
        if player.spread_shot_timer > 0:
            display_text(f"Spread Shot: {player.spread_shot_timer // 60}s", 22, ORANGE, 85, status_y, align="left")
            status_y += 24
        if player.piercing_laser_timer > 0:
            display_text(f"Piercing Laser: {player.piercing_laser_timer // 60}s", 22, PURPLE, 85, status_y, align="left")
            
        # Combo UI
        if combo > 1:
            display_text(f"Combo: {combo}", 36, (255, 120, 120), WIDTH - 20, 58, align="right", bold=True)
            if score_multiplier > 1:
                display_text(f"{score_multiplier}x Multiplier", 26, GOLD, WIDTH - 20, 90, align="right")

        pygame.display.flip()
        clock.tick(FPS)

    final_high = max(score, saved_high)
    save_high_score(final_high)
    save_pilot_score(pilot_name, score)
    game_over_screen(score, final_high, won, pilot_name=pilot_name)

def main():
    pilot_name = "Ace Pilot"
    top_records = get_top_pilots(1)
    if top_records:
        pilot_name = top_records[0][0]

    title_stars = [Star() for _ in range(40)]
    
    while True:
        window.fill(BLACK)
        
        for s in title_stars:
            s.update()
            window.blit(s.image, s.rect)

        display_text("SPACE WARS", 76, (110, 210, 255), WIDTH // 2, HEIGHT // 2 - 120, bold=True)
        display_text("Arcade Sector Defense", 24, GRAY, WIDTH // 2, HEIGHT // 2 - 65)
        
        start_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 - 20, 260, 48)
        pygame.draw.rect(window, (30, 90, 180), start_btn, border_radius=8)
        display_text("START MISSION [SPACE]", 24, WHITE, start_btn.centerx, start_btn.centery, bold=True)
        
        name_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 40, 260, 38)
        pygame.draw.rect(window, DARK_GRAY, name_btn, border_radius=8)
        pygame.draw.rect(window, CYAN, name_btn, 1, border_radius=8)
        display_text(f"Pilot: {pilot_name} [N]", 20, CYAN, name_btn.centerx, name_btn.centery)
        
        hall_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 90, 260, 38)
        pygame.draw.rect(window, DARK_GRAY, hall_btn, border_radius=8)
        pygame.draw.rect(window, GOLD, hall_btn, 1, border_radius=8)
        display_text("Leaderboard / Hall [L]", 20, GOLD, hall_btn.centerx, hall_btn.centery)
        
        display_text("Controls: WASD / Arrows: Move  |  SPACE: Shoot  |  B: Bomb  |  P: Pause", 20, LIGHT_GRAY, WIDTH // 2, HEIGHT - 35)
        pygame.display.flip()

        start_mission = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    start_mission = True
                elif event.key == pygame.K_n:
                    pilot_name = name_input_screen(pilot_name)
                elif event.key == pygame.K_l:
                    leaderboard_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    start_mission = True
                elif name_btn.collidepoint(event.pos):
                    pilot_name = name_input_screen(pilot_name)
                elif hall_btn.collidepoint(event.pos):
                    leaderboard_screen()
                    
        clock.tick(30)

        if start_mission:
            difficulty = difficulty_selection_screen()
            game_loop(difficulty, pilot_name=pilot_name)

if __name__ == "__main__":
    main()
