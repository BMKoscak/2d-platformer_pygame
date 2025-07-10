import pygame
import sys
import random
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# Inicializacija kontrolerjev
pygame.joystick.init()
controllers = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for controller in controllers:
    controller.init()

# Naloži zvočne učinke
hurt_sound = pygame.mixer.Sound("assets/sounds/hurt.wav")
parts_sound = pygame.mixer.Sound("assets/sounds/parts.wav")
jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
ambiance_sound = pygame.mixer.Sound("assets/sounds/Ambiance_Wind_Calm_Loop_Stereo.wav")
walk_sound = pygame.mixer.Sound("assets/sounds/walk.wav")

# Dimenzije zaslona
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Platformer: Skrivnostna pot")

# Dimenzije ploščic
TILE_SIZE = 64

# Load terrain images
terrain_tileset = pygame.image.load("assets/terrain/tilesets.png").convert_alpha()
terrain_tileset = pygame.transform.scale(terrain_tileset, (TILE_SIZE, TILE_SIZE))

# Load parallax background images
bg_images = []
for i in range(1, 6):
    bg_image = pygame.image.load(f"assets/background/plx-{i}.png").convert_alpha()
    bg_images.append(pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)))
bg_width = SCREEN_WIDTH

# Load goal image
goal_image = pygame.image.load("assets/goal/checkpoint.png").convert_alpha()
goal_image = pygame.transform.scale(goal_image, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))

# Load life image
life_image = pygame.image.load("assets/life/life.png").convert_alpha()
life_image = pygame.transform.scale(life_image, (TILE_SIZE // 2, TILE_SIZE // 2))

# Load part images
part_images = [pygame.image.load(f"assets/parts/part_{i}.png").convert_alpha() for i in range(1, 5)]
part_images = [pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) for img in part_images]

# Barve
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Ura igre
clock = pygame.time.Clock()
FPS = 60

# Pisave
pygame.font.init()
font_path = "assets/fonts/PixelifySans-Regular.ttf"
font = pygame.font.Font(font_path, 36)
large_font = pygame.font.Font(font_path, 72)
title_font = pygame.font.Font("assets/fonts/PixelifySans-Bold.ttf", 72)

# Naloži ozadje uvoda
intro_bg = pygame.image.load("assets/intro/intro-bg.jpg").convert()
intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Naloži in predvajaj uvodno glasbo
pygame.mixer.music.load("assets/music/intro.ogg")
pygame.mixer.music.play(-1)

# Nastavitve zvoka
sound_on = True
music_on = True

# Zemljevidi sveta
world_map_1 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                       s                                                                                            ',
    '                              NNNN   XXXXXX                                                                                         ',
    '                              XXXX                           s                                        s                             ',
    '                       XXXXX                                XXXXXXX                               XXXXXXXXXXXXX                     ',
    'P                                                    E                                     XXXX         E                           ',
    '                                                                             E                                                 G    ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

world_map_2 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                          s                                               s                                          ',
    '                                 N    XXXXXXX                                         XXXXXXX                                       ',
    '                              XXXXXX                                    N     XXXXXX                                                ',
    '                   N   XXXXX                     E               N     XXXXX                                                        ',
    '                 XXXX              E                           XXXXXX               E            s                                  ',
    '     XXXXXX     X                                     XXXXXXX                            XXXXXXXXXXXXXXX                            ',
    'P         E    XX     X                        E   X                              XX  XX                E                           ',
    '              XXX      X                          XX                  E                                                   G         ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

world_map_3 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                             s                                                                                      ',
    '                                    N    XXXXXXX  N                                       s                                         ',
    '                               N   XXXX         XXXX                              N   XXXXXXX                                       ',
    '                             XXXX                   XXXX  N                     XXXX                                                ',
    '                 N     XXXX           E                  XXXX   N       N  XXXX        E                                           ',
    '               XXXXXX              E                          XXXX    XXXX                    s                                    ',
    '     XXXXXX   X                                                  XXXX              E     XXXXXXXXXXXXX                             ',
    'P         E  XX       X                        E                                                      E                            ',
    '            XXX        X                                              E                                                   G        ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

current_level = 1
world_maps = [world_map_1, world_map_2, world_map_3]

# Spremenljivke za pomikanje
scroll_x = 0
scroll_speed = 8

# Razredi
class Button:
    def __init__(self, text, x, y, width, height, color, text_color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, self.text_color)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        surface.blit(self.txt_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_text(self, new_text):
        self.text = self.font.render(new_text, True, self.text_color)
        self.text_rect = self.text.get_rect(center=self.rect.center)

# Posodobi razporeditev animacij sovražnikov (2× večja velikost)
enemy_frames = []
for i in range(3):
    frame = pygame.image.load(f"assets/trap/APE1_APE RUNING_{i}.png").convert_alpha()
    frame = pygame.transform.scale(frame, (TILE_SIZE * 2, TILE_SIZE * 2))
    enemy_frames.append(frame)

class Enemy:
    def __init__(self, x, y, width):
        # Posodobljene dimenzije pravokotnika sovražnika
        self.rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * 2)
        self.direction = 1
        self.speed = 2
        self.platform_width = width
        self.start_x = x
        self.frames = enemy_frames
        # Dodaj spremenljivke za sledenje animaciji
        self.frame_index = 0
        self.animation_timer = 0

    def move(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.start_x or self.rect.right >= self.start_x + self.platform_width:
            self.direction *= -1

    def draw(self, surface, scroll_x, dt):
        # Posodobi časovnik animacije z dt (v ms)
        self.animation_timer += dt
        frame_duration = 150  # ms na okvir
        while self.animation_timer >= frame_duration:
            self.animation_timer -= frame_duration
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        image = self.frames[self.frame_index]
        if self.direction == 1:
            image = pygame.transform.flip(image, True, False)
        # Prilagoditev navpičnega poravnanja - poravnava stop sovražnika z vrhom ploščice
        pos = (self.rect.x - scroll_x, self.rect.y + TILE_SIZE - image.get_height())
        surface.blit(image, pos)

class Part:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = random.choice(part_images)
        self.float_direction = 1
        self.float_offset = 0

    def update(self):
        self.float_offset += self.float_direction * 0.5
        if abs(self.float_offset) >= 5:
            self.float_direction *= -1

    def draw(self, surface, scroll_x):
        pos = (self.rect.x - scroll_x, self.rect.y + self.float_offset)
        surface.blit(self.image, pos)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.velocity = [0, 0]
        self.on_ground = False
        self.lives = 3
        self.collected_parts = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.speed = 7
        self.jump_strength = 22
        self.gravity = 1.0
        self.max_fall_speed = 18
        self.spawn_point = (x, y)
        self.invulnerable_duration = FPS * 2
        # Dodaj lastnosti za animacijo in smer
        self.state = "idle"  # stanja: idle, walk, jump, fall, win, lose, hurt
        self.animations = self.load_player_animations()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100  # ms na okvir
        self.facing_right = True
        # Dodaj časovnik za poškodbe (v milisekundah)
        self.hurt_timer = 0
        self.controller_deadzone = 0.2  # Dodaj mrtvo območje za analogno palico

    def load_player_animations(self):
        animations = {}
        # win (spritesheet: win.png, frame 92x63, image size 1152x64)
        win_sheet = pygame.image.load("assets/player/win/win.png").convert_alpha()
        animations["win"] = self.split_spritesheet(win_sheet, 92, 63)
        # idle (4 individualni okviri)
        idle_frames = []
        for i in range(1, 5):
            img = pygame.image.load(f"assets/player/idle/idle-{i}.png").convert_alpha()
            idle_frames.append(img)
        animations["idle"] = idle_frames
        # walk (10 individualnih okvirjev)
        walk_frames = []
        for i in range(1, 11):
            img = pygame.image.load(f"assets/player/walk/walk_{i}.png").convert_alpha()
            walk_frames.append(img)
        animations["walk"] = walk_frames
        # fall (4 individualni okviri)
        fall_frames = []
        for i in range(1, 5):
            img = pygame.image.load(f"assets/player/fall/fall-{i}.png").convert_alpha()
            fall_frames.append(img)
        animations["fall"] = fall_frames
        # jump (spritesheet: jump.png, frame 86x64, image size 576x64)
        jump_sheet = pygame.image.load("assets/player/jump/jump.png").convert_alpha()
        animations["jump"] = self.split_spritesheet(jump_sheet, 86, 64)
        # lose (spritesheet: lose.png, frame 98x64, image size 1728x64)
        lose_sheet = pygame.image.load("assets/player/lose/lose.png").convert_alpha()
        animations["lose"] = self.split_spritesheet(lose_sheet, 98, 64)
        # Dodaj animacije za poškodbe
        hurt_frames = []
        for i in range(1, 4):
            img = pygame.image.load(f"assets/player/hurt/hurt_{i}.png").convert_alpha()
            hurt_frames.append(img)
        animations["hurt"] = hurt_frames
        return animations

    def split_spritesheet(self, sheet, frame_width, frame_height):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        for i in range(sheet_width // frame_width):
            frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

    def update_animation(self, dt):
        self.animation_timer += dt
        while self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])

    def draw(self, surface, scroll, dt):
        # Določi pravilno stanje
        if self.hurt_timer > 0:
            new_state = "hurt"
            self.hurt_timer = max(0, self.hurt_timer - dt)
        else:
            if not self.on_ground:
                new_state = "jump" if self.velocity[1] < 0 else "fall"
            else:
                new_state = "walk" if abs(self.velocity[0]) > 0 else "idle"

        # Ponastavi indeks animacije, če se stanje spremeni
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

        self.update_animation(dt)
        current_image = self.animations[self.state][self.frame_index]
        
        # Povečaj sliko
        scaled_image = pygame.transform.scale(current_image, (current_image.get_width()*2, current_image.get_height()*2))
        if not self.facing_right:
            scaled_image = pygame.transform.flip(scaled_image, True, False)

        # Izračunaj centrirano pozicijo
        x = self.rect.x - scroll - (scaled_image.get_width() - self.rect.width) // 2
        y = self.rect.bottom - scaled_image.get_height()

        surface.blit(scaled_image, (x, y))

    def is_dead(self):
        return self.lives <= 0

    def move(self, keys, tiles, controller=None):
        dx = 0
        dy = 0

        # Kontrole s tipkovnico
        if keys[K_LEFT]:
            dx = -self.speed
            self.facing_right = False
        if keys[K_RIGHT]:
            dx = self.speed
            self.facing_right = True

        # Kontrole s kontrolerjem
        if controller:
            analog_x = controller.get_axis(0)
            if abs(analog_x) > self.controller_deadzone:
                dx = self.speed * analog_x
                self.facing_right = analog_x > 0

            if controller.get_button(0) and self.on_ground:
                self.velocity[1] = -self.jump_strength
                self.on_ground = False
                if sound_on:
                    jump_sound.play()

        # Skok s tipkovnico
        if keys[K_UP] and self.on_ground:
            self.velocity[1] = -self.jump_strength
            self.on_ground = False
            if sound_on:
                jump_sound.play()

        # Shrani horizontalno gibanje za zaznavanje stanja animacije
        self.velocity[0] = dx

        self.velocity[1] += self.gravity
        if self.velocity[1] > self.max_fall_speed:
            self.velocity[1] = self.max_fall_speed

        dy = self.velocity[1]

        self.handle_collision(tiles, dx, dy)

        self.check_on_ground(tiles)

    def handle_collision(self, tiles, dx, dy):
        self.rect.x += dx
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                if dx > 0:
                    self.rect.right = tile['rect'].left
                elif dx < 0:
                    self.rect.left = tile['rect'].right

        self.rect.y += dy
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                if dy > 0:
                    self.rect.bottom = tile['rect'].top
                    self.velocity[1] = 0
                    self.on_ground = True
                elif dy < 0:
                    self.rect.top = tile['rect'].bottom
                    self.velocity[1] = 0

    def check_on_ground(self, tiles):
        self.rect.y += 1
        on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                on_ground = True
                break
        self.rect.y -= 1
        self.on_ground = on_ground

    def update_invulnerability(self):
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.invulnerable_timer = 0

    def respawn(self):
        self.rect.topleft = self.spawn_point
        self.velocity = [0, 0]
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration

    def check_collision(self, tiles, traps, parts, goal, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if not self.invulnerable:
                    return 'hit_enemy'

        for trap in traps:
            if self.rect.colliderect(trap):
                if not self.invulnerable:
                    return 'hit_trap'

        for part in parts[:]:
            if self.rect.colliderect(part.rect):
                parts.remove(part)
                self.collected_parts += 1
                return 'collected'

        if goal and self.rect.colliderect(goal) and self.collected_parts >= 3:
            return 'level_complete'

        return 'none'

# Funkcije
def draw_map(world_map, existing_parts=None):
    tiles = []
    traps = []
    parts = existing_parts if existing_parts is not None else []
    goal = None
    enemies = []

    for row_index, row in enumerate(world_map):
        platform_start = None
        last_enemy_x = -float('inf')
        for col_index, col in enumerate(row):
            x = col_index * TILE_SIZE
            y = SCREEN_HEIGHT - (len(world_map) - row_index) * TILE_SIZE
            if col == 'X':
                tiles.append({
                    'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE),
                    'sprite': terrain_tileset
                })
                if platform_start is None:
                    platform_start = x
            elif col == ' ' and platform_start is not None:
                platform_width = x - platform_start
                if platform_width >= TILE_SIZE * 4:
                    # Check if there's an 'N' above the current platform
                    platform_start_idx = platform_start // TILE_SIZE
                    platform_end_idx = col_index
                    no_spawn_zone = False
                    
                    # Check the row above for 'N' characters
                    if row_index > 0:
                        for check_idx in range(platform_start_idx, platform_end_idx):
                            if world_map[row_index - 1][check_idx] == 'N':
                                no_spawn_zone = True
                                break
                    
                    # Only spawn enemy if not in no-spawn zone and far enough from last enemy
                    if not no_spawn_zone and x - last_enemy_x > TILE_SIZE * 8:
                        enemies.append(Enemy(platform_start, y - TILE_SIZE, platform_width))
                        last_enemy_x = x
                platform_start = None
            elif col == 't':
                traps.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif col == 's' and (existing_parts is None or not any(part.rect.colliderect(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)) for part in existing_parts)):
                parts.append(Part(x, y))
            elif col == 'G':
                goal = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                continue  # Remove checkpoint handling

    return tiles, traps, parts, goal, enemies

def draw_intro():
    screen.blit(intro_bg, (0, 0))

    shadow_offset = 3
    shadow_color = (0, 0, 0, 128)

    shadow_text = title_font.render("Skrivnostna pot", True, shadow_color)
    shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + shadow_offset, SCREEN_HEIGHT // 4 + shadow_offset))

    shadow_surface = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
    shadow_surface.blit(shadow_text, (0, 0))

    screen.blit(shadow_surface, shadow_rect)

    title = title_font.render("Skrivnostna pot", True, WHITE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title, title_rect)

    button_width = 300
    button_height = 60
    button_spacing = 20

    start_button = Button("Prični z igro", 
                          SCREEN_WIDTH // 2 - button_width // 2, 
                          SCREEN_HEIGHT // 2, 
                          button_width, button_height, 
                          (0, 100, 0), WHITE, (0, 150, 0), font)

    music_text = "Glasba: ON" if music_on else "Glasba: OFF"
    music_button = Button(music_text,
                          SCREEN_WIDTH // 2 - button_width // 2, 
                          SCREEN_HEIGHT // 2 + button_height + button_spacing, 
                          button_width, button_height, 
                          (100, 180, 255), BLACK, (150, 200, 255), font)

    sound_text = "Zvočni učinki: ON" if sound_on else "Zvočni učinki: OFF"
    sound_button = Button(sound_text,
                          SCREEN_WIDTH // 2 - button_width // 2, 
                          SCREEN_HEIGHT // 2 + 2 * (button_height + button_spacing), 
                          button_width, button_height, 
                          (100, 180, 255), BLACK, (150, 200, 255), font)

    # Add controls button
    controls_button = Button("Tipke", 
                           SCREEN_WIDTH // 2 - button_width // 2, 
                           SCREEN_HEIGHT // 2 + 3 * (button_height + button_spacing), 
                           button_width, button_height, 
                           (100, 180, 255), BLACK, (150, 200, 255), font)

    start_button.draw(screen)
    music_button.draw(screen)
    sound_button.draw(screen)
    controls_button.draw(screen)

    pygame.display.flip()

    return start_button, music_button, sound_button, controls_button

def draw_text_screen(text, duration=2000):
    screen.fill(WHITE)
    message = font.render(text, True, BLACK)
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(duration)

def draw_message(text, color=BLACK):
    message = font.render(text, True, color)
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    screen.blit(message, message_rect)

def reset_game_state(level):
    player = Player(TILE_SIZE, SCREEN_HEIGHT - 2 * TILE_SIZE)
    tiles, traps, parts, goal, enemies = draw_map(world_maps[level - 1])
    return player, tiles, traps, parts, goal, enemies

def play_mini_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 72)
    clock = pygame.time.Clock()

    number = random.randint(0, 9)
    text = font.render(f"Pritisni številko {number}, da končaš popravilo letala.", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    screen.fill(WHITE)
    screen.blit(text, text_rect)
    pygame.display.flip()

    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < 3000:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.unicode == str(number):
                    return True

        clock.tick(60)

    return False

# Posodobi za brezšivno ploščanje vsake plasti ozadja.
def draw_bg(scroll):
    for i, bg in enumerate(bg_images):
        speed = 0.2 * (i + 1)
        offset = int(-(scroll * speed)) % SCREEN_WIDTH
        screen.blit(bg, (offset - SCREEN_WIDTH, 0))
        screen.blit(bg, (offset, 0))

def draw_lives(surface, lives, x, y):
    for i in range(lives):
        surface.blit(life_image, (x + i * (TILE_SIZE // 2 + 5), y))

def draw_controls_screen():
    screen.fill(BLACK)
    controls = [
        "=== Tipkovnica ===",
        "Puščice - Premikanje",
        "Puščica gor - Skok",
        "E - Interakcija",
        "",
        "=== Kontroler ===",
        "Leva palica - Premikanje",
        "A - Skok",
        "X - Interakcija",
        "",
        "Pritisni ESC za vrnitev"
    ]
    
    y_offset = SCREEN_HEIGHT // 4
    for line in controls:
        text = font.render(line, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 50
    
    pygame.display.flip()

def main():
    global sound_on, music_on
    game_state = "intro"
    in_controls = False
    current_level = 1
    player, tiles, traps, parts, goal, enemies = reset_game_state(current_level)

    start_button, music_button, sound_button, controls_button = None, None, None, None
    last_footstep_time = 0
    footstep_delay = 300

    running = True
    scroll = 0
    while running:
        dt = clock.tick(FPS)
        
        controller = controllers[0] if controllers else None

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE and in_controls:
                in_controls = False
                game_state = "intro"
            elif event.type == MOUSEBUTTONDOWN and game_state == "intro":
                if start_button and start_button.is_clicked(event.pos):
                    game_state = "playing"
                    if music_on:
                        pygame.mixer.music.load("assets/music/glasba_ozadje.mp3")
                        pygame.mixer.music.play(-1)
                elif music_button and music_button.is_clicked(event.pos):
                    music_on = not music_on
                    music_text = "Glasba: ON" if music_on else "Glasba: OFF"
                    music_button.update_text(music_text)
                    if music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif sound_button and sound_button.is_clicked(event.pos):
                    sound_on = not sound_on
                    sound_text = "Zvočni učinki: ON" if sound_on else "Zvočni učinki: OFF"
                    sound_button.update_text(sound_text)
                elif controls_button and controls_button.is_clicked(event.pos):
                    in_controls = True
                    draw_controls_screen()
            elif (event.type == KEYDOWN or 
                  (controller and event.type == JOYBUTTONDOWN)) and game_state == "playing":
                handle_interaction = False
                
                if event.type == KEYDOWN and event.key == K_e:
                    handle_interaction = True
                elif controller and event.type == JOYBUTTONDOWN and event.button == 2:
                    handle_interaction = True
                
                if handle_interaction and player.rect.colliderect(goal) and player.collected_parts >= 3:
                    if current_level < 3:
                        current_level += 1
                        player, tiles, traps, parts, goal, enemies = reset_game_state(current_level)
                        player.collected_parts = 0
                    elif current_level == 3:
                        if play_mini_game():
                            game_state = "game_complete"
                        else:
                            draw_text_screen("Popravilo letala ni bilo uspešno, opice so te ujele!", 2000)
                            game_state = "game_over"

        if game_state == "intro" and not in_controls:
            start_button, music_button, sound_button, controls_button = draw_intro()
            
            if controller:
                if controller.get_button(0):
                    game_state = "playing"
                    if music_on:
                        pygame.mixer.music.load("assets/music/glasba_ozadje.mp3")
                        pygame.mixer.music.play(-1)
                elif controller.get_button(1):
                    music_on = not music_on
                    music_text = "Glasba: ON" if music_on else "Glasba: OFF"
                    music_button.update_text(music_text)
                    if music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif controller.get_button(2):
                    sound_on = not sound_on
                    sound_text = "Zvočni učinki: ON" if sound_on else "Zvočni učinki: OFF"
                    sound_button.update_text(sound_text)

        elif game_state == "playing":

            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            player.move(keys, tiles, controller)
            
            is_moving = (keys[K_LEFT] or keys[K_RIGHT] or 
                        (controller and abs(controller.get_axis(0)) > player.controller_deadzone))
            
            if is_moving and player.on_ground and sound_on:
                if current_time - last_footstep_time >= footstep_delay:
                    walk_sound.play()
                    last_footstep_time = current_time

            player.update_invulnerability()

            for enemy in enemies:
                enemy.move()

            for part in parts:
                part.update()

            collision_result = player.check_collision(tiles, traps, parts, goal, enemies)

            if collision_result == 'collected' and sound_on:
                parts_sound.play()

            if collision_result == 'hit_enemy' and not player.invulnerable:
                if player.hurt_timer == 0:
                    player.hurt_timer = 300

            if collision_result in ['hit_trap', 'hit_enemy']:
                if collision_result == 'hit_enemy' and sound_on:
                    hurt_sound.play()
                if not player.invulnerable:
                    player.lives -= 1
                    player.invulnerable = True
                    player.invulnerable_timer = FPS * 2
                    if player.lives <= 0:
                        game_state = "game_over"

            player.update_invulnerability()

            level_width = len(world_maps[current_level - 1][0]) * TILE_SIZE
            player.rect.x = max(0, min(player.rect.x, level_width - player.rect.width))
            
            if player.rect.top > SCREEN_HEIGHT:
                player.respawn()

            desired_scroll = player.rect.centerx - SCREEN_WIDTH // 2
            scroll += (desired_scroll - scroll) * 0.1
            level_width = len(world_maps[current_level - 1][0]) * TILE_SIZE
            scroll = max(0, min(scroll, level_width - SCREEN_WIDTH))
            
            level_top = SCREEN_HEIGHT - len(world_maps[current_level - 1]) * TILE_SIZE
            level_bottom = SCREEN_HEIGHT - player.rect.height
            player.rect.y = max(level_top, min(player.rect.y, level_bottom))
            
            draw_bg(scroll)

            for enemy in enemies:
                enemy.draw(screen, scroll, dt)

            for tile in tiles:
                screen.blit(terrain_tileset, 
                           (tile['rect'].x - scroll, tile['rect'].y),
                           (0, 0, TILE_SIZE, TILE_SIZE))
            for trap in traps:
                pygame.draw.rect(screen, RED, trap.move(-scroll, 0))
            for part in parts:
                part.draw(screen, scroll)
            if goal:
                goal_pos = (goal.x - scroll - TILE_SIZE * 0.25, goal.y - goal_image.get_height() + TILE_SIZE)
                screen.blit(goal_image, goal_pos)
            player.draw(screen, scroll, dt)

            draw_lives(screen, player.lives, 10, 10)
            parts_text = font.render(f"Zbrani deli: {player.collected_parts}/3", True, WHITE)
            level_text = font.render(f"Nivo: {current_level}", True, WHITE)
            screen.blit(parts_text, (10, 50))
            screen.blit(level_text, (10, 90))

            if goal and player.rect.colliderect(goal):
                if player.collected_parts >= 3:
                    if current_level < 3:
                        draw_message(f"Pritisni E za nadaljevanje v {current_level + 1}. nivo!", WHITE)
                    else:
                        draw_message("Pritisni E za končni izziv!", WHITE)
                else:
                    draw_message("Nimaš vseh delov letala, prosim zberi vse dele letala za nadaljevanje!", WHITE)

            if sound_on and random.random() < 0.001:
                ambiance_sound.play()

        elif game_state == "game_over":
            draw_text_screen("Konec igre, izgubil si!")
            pygame.time.wait(2000)
            current_level = 1
            player, tiles, traps, parts, goal, enemies = reset_game_state(current_level)
            game_state = "intro"

        elif game_state == "game_complete":
            draw_text_screen("Čestitamo! Dokončali ste igro!")
            pygame.time.wait(2000)
            current_level = 1
            player, tiles, traps, parts, goal, enemies = reset_game_state(current_level)
            game_state = "intro"


        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()