import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
PURPLE = (150, 0, 255)
FPS = 60

# Screen setup
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Wars')
clock = pygame.time.Clock()

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

# Display text on the screen
def display_text(text, size, color, x, y, surface=window):
    font = pygame.font.SysFont(None, size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(x, y))
    surface.blit(rendered_text, text_rect)

# High score management
def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try: return int(f.read())
            except ValueError: return 0
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# --- SPRITE CLASSES ---

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
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        if self.type == 'shield':
            pygame.draw.circle(self.image, CYAN, (10, 10), 10)
        elif self.type == 'rapid_fire':
            pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        elif self.type == 'bomb':
            pygame.draw.circle(self.image, WHITE, (10, 10), 10)
        elif self.type == 'spread_shot':
            pygame.draw.circle(self.image, (255, 150, 0), (10, 10), 10) # Orange
        elif self.type == 'piercing_laser':
            pygame.draw.circle(self.image, PURPLE, (10, 10), 10)
        else: # life
            pygame.draw.circle(self.image, RED, (10, 10), 10)
        
        # Inner white circle
        pygame.draw.circle(self.image, WHITE, (10, 10), 6)
        
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
        self.boss_mode_active = False # New flag to track if the player has been empowered

    def update_state(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH // 2:
            self.rect.x += self.speed
        
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
                self.image = pygame.Surface((50,30), pygame.SRCALPHA)
            else:
                self.image = self.image_original
        else:
            self.image = self.image_original

    def shoot(self, all_sprites, bullets):
        delay = 5 if self.rapid_fire_timer > 0 else self.shoot_delay
        if self.last_shot >= delay:
            is_piercing = self.piercing_laser_timer > 0
            bullet_speed = 15 if is_piercing else 10
            
            # Check if player is empowered for boss fight or has spread shot
            if self.boss_mode_active or self.spread_shot_timer > 0:
                for vy in [-2, 0, 2]:
                    bullet = Bullet(self.rect.right, self.rect.centery, bullet_speed, piercing=is_piercing)
                    bullet.speed_y = vy  # Angled shots
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            else:
                bullet = Bullet(self.rect.right, self.rect.centery, bullet_speed, piercing=is_piercing)
                all_sprites.add(bullet)
                bullets.add(bullet)
                
            self.last_shot = 0
            
    def take_damage(self):
        if self.invulnerable_timer == 0:
            if self.has_shield:
                self.has_shield = False
                self.invulnerable_timer = 60 # 1 sec invuln
            else:
                self.lives -= 1
                self.invulnerable_timer = 90 # 1.5 secs invuln
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
            self.image = pygame.Surface((15, 5))
            self.image.fill(PURPLE)
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

def difficulty_selection_screen():
    window.fill(BLACK)
    display_text("Select Difficulty", 55, WHITE, WIDTH // 2, HEIGHT // 2 - 80)

    easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)
    medium_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    hard_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    pygame.draw.rect(window, GRAY, easy_button, border_radius=10)
    pygame.draw.rect(window, GRAY, medium_button, border_radius=10)
    pygame.draw.rect(window, GRAY, hard_button, border_radius=10)
    
    display_text("Easy", 30, WHITE, easy_button.centerx, easy_button.centery)
    display_text("Medium", 30, WHITE, medium_button.centerx, medium_button.centery)
    display_text("Hard", 30, WHITE, hard_button.centerx, hard_button.centery)

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

def game_over_screen(score, high_score, won=False):
    window.fill(BLACK)
    if won:
        display_text("YOU WIN!", 75, GREEN, WIDTH // 2, HEIGHT // 2 - 80)
    else:
        display_text("Game Over", 65, RED, WIDTH // 2, HEIGHT // 2 - 80)
        
    display_text(f"Score: {score}", 40, WHITE, WIDTH // 2, HEIGHT // 2 - 10)
    display_text(f"High Score: {high_score}", 40, YELLOW, WIDTH // 2, HEIGHT // 2 + 30)

    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
    pygame.draw.rect(window, GRAY, restart_button, border_radius=10)
    display_text("Restart", 30, WHITE, restart_button.centerx, restart_button.centery)
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    return

# --- MAIN GAME LOOP ---

def game_loop(difficulty):
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
    
    combo = 0
    combo_timer = 0
    score_multiplier = 1

    for _ in range(max_asteroids):
        asteroid = Asteroid(ast_spd)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    score = 0
    high_score = load_high_score()
    running = True
    boss_active = False
    boss = None
    won = False
    
    # 1000 Score to trigger Boss Battle!
    BOSS_THRESHOLD = 1000
    
    def spawn_powerup(x, y):
        if random.random() < 0.15:
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
                if event.key == pygame.K_b and player.bombs > 0 and not boss_active:
                    player.bombs -= 1
                    bomb_flash_timer = 10
                    shake_timer = 30
                    for e in enemies:
                        create_explosion(e.rect.centerx, e.rect.centery, RED, 20, all_sprites, particles)
                        score += 50 * score_multiplier
                        combo += 1
                        e.kill()
                    for ast in asteroids:
                        create_explosion(ast.rect.centerx, ast.rect.centery, GRAY, 10, all_sprites, particles)
                        score += 5 * score_multiplier
                        combo += 1
                        ast.kill()
                    combo_timer = 180

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            player.shoot(all_sprites, player_bullets)
            
        # Engine particles
        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            p = Particle(player.rect.left + 5, player.rect.centery + random.randint(-5, 5), (255, random.randint(100, 200), 0))
            p.vx = -random.uniform(3, 6)
            p.vy = random.uniform(-1, 1)
            all_sprites.add(p)
            particles.add(p)

        # Triggers Boss Phase
        if score >= BOSS_THRESHOLD and not boss_active:
            boss_active = True
            boss = Boss()
            all_sprites.add(boss)
            
            # Spawn a powerup as soon as the boss enters!
            spawn_powerup((WIDTH // 2) + 100, HEIGHT // 2)
            # Guarantee a drop for balance by forcing it
            guaranteed_pu = PowerUp((WIDTH // 2) + 100, HEIGHT // 2)
            all_sprites.add(guaranteed_pu)
            powerups.add(guaranteed_pu)
            
            # POWER UP THE PLAYER!
            player.boss_mode_active = True
            player.lives = max(player.lives, 3) # Give them at least some health back
            
            # Kill regular enemies & asteroids to focus on Boss
            for e in enemies:
                create_explosion(e.rect.centerx, e.rect.centery, RED, 15, all_sprites, particles)
                e.kill()
            for ast in asteroids:
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
        player.update_state(keys)

        if boss_active and boss:
            boss.update_state(player.rect.centery, all_sprites, enemy_bullets)
        else:
            asteroids.update()
            for e in enemies:
                e.update_state(player.rect.centerx, player.rect.centery, all_sprites, enemy_bullets)

        # Mechanics When Boss Is NOT Active
        if not boss_active:
            # Asteroid respawning points
            for asteroid in list(asteroids):
                if asteroid.rect.right < 0:
                    asteroid.kill()
                    score += 10
            
            # Enemies moving off screen
            for e in list(enemies):
                if e.rect.right < 0:
                    e.kill()
            
            # Player bullets hit enemies
            # Check collisions manually to account for piercing
            for e in list(enemies):
                hit_bullets = pygame.sprite.spritecollide(e, player_bullets, False)
                if hit_bullets:
                    for b in hit_bullets:
                        if not b.piercing:
                            b.kill()
                    score += 50 * score_multiplier
                    combo += 1
                    combo_timer = 180
                    score_multiplier = min(5, 1 + (combo // 5))
                    create_explosion(e.rect.centerx, e.rect.centery, RED, 20, all_sprites, particles)
                    spawn_powerup(e.rect.centerx, e.rect.centery)
                    e.kill()
                
            # Maintain enemies
            if len(enemies) < (2 if score > 150 else 1):
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
                    score += 5 * score_multiplier
                    combo += 1
                    combo_timer = 180
                    score_multiplier = min(5, 1 + (combo // 5))
                    create_explosion(ast.rect.centerx, ast.rect.centery, GRAY, 10, all_sprites, particles)
                    spawn_powerup(ast.rect.centerx, ast.rect.centery)
                    ast.kill()
            
            # Maintain asteroid count
            while len(asteroids) < max_asteroids:
                new_asteroid = Asteroid(ast_spd)
                all_sprites.add(new_asteroid)
                asteroids.add(new_asteroid)

        # Mechanics When Boss IS Active
        if boss_active and boss and boss.state == 'fighting':
            # Player bullets hit boss
            if pygame.sprite.spritecollide(boss, player_bullets, True):
                boss.health -= 1
                if boss.health <= 0:
                    score += 1000
                    create_explosion(boss.rect.centerx, boss.rect.centery, PURPLE, 100, all_sprites, particles)
                    boss.kill()
                    shake_timer = 60
                    won = True
                    running = False

        # Collect Powerups
        collected = pygame.sprite.spritecollide(player, powerups, True)
        for pu in collected:
            if pu.type == 'shield':
                player.has_shield = True
            elif pu.type == 'rapid_fire':
                player.rapid_fire_timer = 300 # 5 seconds
            elif pu.type == 'life':
                player.lives = min(player.lives + 1, 5)
            elif pu.type == 'bomb':
                player.bombs = min(player.bombs + 1, 3)
            elif pu.type == 'spread_shot':
                player.spread_shot_timer = 300
            elif pu.type == 'piercing_laser':
                player.piercing_laser_timer = 300

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

        # Draw to game_surface instead of window
        all_sprites.draw(game_surface)
        
        # Draw Boss Health Bar
        if boss_active and boss and boss.state == 'fighting':
            bar_width = 400
            bar_height = 20
            health_ratio = max(0, boss.health / boss.max_health)
            pygame.draw.rect(game_surface, GRAY, (WIDTH//2 - bar_width//2, 20, bar_width, bar_height))
            pygame.draw.rect(game_surface, RED, (WIDTH//2 - bar_width//2, 20, int(bar_width * health_ratio), bar_height))
            display_text("BOSS", 25, WHITE, WIDTH//2, 10, surface=game_surface)

        # Draw Shield Effect
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
            # Alpha goes from 255 (opaque) to 0 over 10 frames
            alpha = int(255 * (bomb_flash_timer / 10))
            flash_surface.set_alpha(alpha)
            flash_surface.fill(WHITE)
            window.blit(flash_surface, (0, 0))
            bomb_flash_timer -= 1

        # UI
        display_text(f"Score: {score}", 30, WHITE, 80, 20)
        display_text(f"High Score: {high_score}", 30, YELLOW, WIDTH - 120, 20)
        
        # Display Lives
        display_text("Lives: ", 30, WHITE, WIDTH // 2 - 50, HEIGHT - 20)
        for i in range(player.lives):
            window.blit(mini_player_img, (WIDTH // 2 - 5 + i * 30, HEIGHT - 30))
            
        # Display Bombs
        display_text(f"Bombs: {player.bombs}", 30, WHITE, WIDTH // 2 - 200, HEIGHT - 20)
            
        # UI for Active Power-ups
        status_y = 50
        if player.rapid_fire_timer > 0:
            display_text(f"Rapid Fire: {player.rapid_fire_timer // 60}s", 25, YELLOW, 90, status_y)
            status_y += 25
        if player.spread_shot_timer > 0:
            display_text(f"Spread Shot: {player.spread_shot_timer // 60}s", 25, (255, 150, 0), 90, status_y)
            status_y += 25
        if player.piercing_laser_timer > 0:
            display_text(f"Piercing Laser: {player.piercing_laser_timer // 60}s", 25, PURPLE, 90, status_y)
            
        # Combo UI
        if combo > 1:
            display_text(f"Combo: {combo}", 40, (255, 100, 100), WIDTH - 120, 60)
            if score_multiplier > 1:
                display_text(f"Multiplier: {score_multiplier}x", 30, YELLOW, WIDTH - 120, 90)

        pygame.display.flip()
        clock.tick(FPS)

    save_high_score(max(score, high_score))
    game_over_screen(score, max(score, high_score), won)

def main():
    while True:
        window.fill(BLACK)
        display_text("SPACE WARS", 70, (100, 200, 255), WIDTH // 2, HEIGHT // 2 - 60)
        display_text("Press SPACE to Start", 35, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
        display_text("Arrow Keys: Move | SPACE: Shoot", 25, GRAY, WIDTH // 2, HEIGHT - 50)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False

        difficulty = difficulty_selection_screen()
        game_loop(difficulty)

if __name__ == "__main__":
    main()
