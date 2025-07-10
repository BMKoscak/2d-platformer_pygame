# =============================================================================
# Platformer: The Mysterious Path
#
# Author: The Benn/BMKoscak
# Version: 1.0.0
#
# A simple platformer game built with Pygame.
# The player must navigate through levels, collect parts, avoid enemies,
# and reach the goal to repair their plane.
# =============================================================================

import pygame
import sys
import random
from pygame.locals import *

# --- Initialization ---
pygame.init()
pygame.mixer.init() # Initialize the mixer for sound effects

# --- Controller Setup ---
# Initialize the joystick module to handle game controllers
pygame.joystick.init()
# Create a list of all connected joystick/controller devices
controllers = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
# Initialize each detected controller
for controller in controllers:
    controller.init()

# --- Load Sound Effects ---
# It's good practice to wrap asset loading in try-except blocks in a real release
# to handle missing files gracefully. For simplicity, we'll load them directly.
try:
    hurt_sound = pygame.mixer.Sound("assets/sounds/hurt.wav")
    parts_sound = pygame.mixer.Sound("assets/sounds/parts.wav")
    jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
    ambiance_sound = pygame.mixer.Sound("assets/sounds/Ambiance_Wind_Calm_Loop_Stereo.wav")
    walk_sound = pygame.mixer.Sound("assets/sounds/walk.wav")
except pygame.error as e:
    print(f"Error loading sound assets: {e}")
    # Create dummy sound objects if loading fails so the game doesn't crash
    class DummySound:
        def play(self): pass
    hurt_sound = parts_sound = jump_sound = ambiance_sound = walk_sound = DummySound()


# --- Screen and Display Setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
# Use DOUBLEBUF for smoother rendering, especially with many moving elements
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Platformer: The Mysterious Path")

# --- Game Constants ---
TILE_SIZE = 64
FPS = 60

# --- Load Image Assets ---
# Using a function to load and scale images can reduce code repetition.
def load_and_scale_image(path, size):
    """Loads an image, converts it for performance, and scales it."""
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        # Return a placeholder surface if the image is missing
        placeholder = pygame.Surface(size)
        placeholder.fill((255, 0, 255)) # Use a bright color to easily spot missing assets
        return placeholder

# Load terrain tileset
terrain_tileset = load_and_scale_image("assets/terrain/tilesets.png", (TILE_SIZE, TILE_SIZE))

# Load parallax background images
bg_images = []
for i in range(1, 6):
    bg_image = pygame.image.load(f"assets/background/plx-{i}.png").convert_alpha()
    bg_images.append(pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)))

# Load other game assets
goal_image = load_and_scale_image("assets/goal/checkpoint.png", (int(TILE_SIZE * 1.5), int(TILE_SIZE * 1.5)))
life_image = load_and_scale_image("assets/life/life.png", (TILE_SIZE // 2, TILE_SIZE // 2))
part_images = [load_and_scale_image(f"assets/parts/part_{i}.png", (TILE_SIZE, TILE_SIZE)) for i in range(1, 5)]

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Game Clock ---
clock = pygame.time.Clock()

# --- Font Initialization ---
pygame.font.init()
# Using a single font file path variable makes it easy to change fonts later
try:
    font_path = "assets/fonts/PixelifySans-Regular.ttf"
    bold_font_path = "assets/fonts/PixelifySans-Bold.ttf"
    font = pygame.font.Font(font_path, 36)
    large_font = pygame.font.Font(font_path, 72)
    title_font = pygame.font.Font(bold_font_path, 72)
except FileNotFoundError:
    print("Font files not found, using default Pygame font.")
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    title_font = pygame.font.Font(None, 80)


# --- Intro Screen Assets ---
intro_bg = pygame.image.load("assets/intro/intro-bg.jpg").convert()
intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Music and Sound Settings ---
try:
    pygame.mixer.music.load("assets/music/intro.ogg")
    pygame.mixer.music.play(-1) # Play intro music on a loop
except pygame.error as e:
    print(f"Could not load intro music: {e}")

sound_on = True
music_on = True

# --- World Maps ---
# 'P' = Player Start, 'X' = Tile, 'E' = Enemy (on platform above), 's' = Part
# 'G' = Goal, 't' = Trap, 'N' = No enemy spawn zone above this point
world_map_1 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                     s                                                                                                              ',
    '               NNNN   XXXXXX                                                                                                        ',
    '               XXXX                               s                                     s                                           ',
    '                     XXXXX                                XXXXXXX                                     XXXXXXXXXXXXX                   ',
    'P                                             E                                   XXXX       E                                     ',
    '                                                                       E                                                    G       ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

world_map_2 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                           s                                                 s                                                      ',
    '                     N    XXXXXXX                                          XXXXXXX                                                   ',
    '                   XXXXXX                                           N    XXXXXX                                                     ',
    '             N   XXXXX                   E                    N    XXXXX                                                           ',
    '           XXXX           E                                  XXXXXX             E            s                                     ',
    '     XXXXXX     X                                      XXXXXXX                                 XXXXXXXXXXXXXXX                       ',
    'P       E     XX    X                         E     X                                    XX  XX                E                    ',
    '             XXX     X                               XX                     E                                             G         ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

world_map_3 = [
    '                                                                                                                                    ',
    '                                                                                                                                    ',
    '                                 s                                                                                                  ',
    '                           N    XXXXXXX   N                                          s                                               ',
    '                     N   XXXX        XXXX                                     N   XXXXXXX                                           ',
    '                   XXXX              XXXX   N                             XXXX                                                      ',
    '             N    XXXX       E              XXXX   N      N  XXXX       E                                                          ',
    '           XXXXXX           E                      XXXX    XXXX                  s                                                 ',
    '     XXXXXX   X                                            XXXX           E     XXXXXXXXXXXXX                                     ',
    'P       E     XX      X                         E                                              E                                  ',
    '             XXX       X                                         E                                                      G         ',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

# List of all level maps for easy access
world_maps = [world_map_1, world_map_2, world_map_3]

# --- Game Classes ---

class Button:
    """A simple clickable button class for UI elements."""
    def __init__(self, text, x, y, width, height, color, text_color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.text = text
        self.font = font
        self.is_hovered = False
        self.render_text()

    def render_text(self):
        """Renders the button's text to a surface."""
        self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw(self, surface):
        """Draws the button on the given surface."""
        # Change color on hover for better user feedback
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        surface.blit(self.txt_surface, text_rect)

    def check_hover(self, pos):
        """Checks if the mouse position is over the button."""
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        """Checks if the button was clicked at the given position."""
        return self.rect.collidepoint(pos)

    def update_text(self, new_text):
        """Updates the button's text and re-renders it."""
        self.text = new_text
        self.render_text()

# Pre-load enemy animation frames to avoid loading them repeatedly
enemy_frames = [load_and_scale_image(f"assets/trap/APE1_APE RUNING_{i}.png", (TILE_SIZE * 2, TILE_SIZE * 2)) for i in range(3)]

class Enemy:
    """Represents a moving enemy that patrols a platform."""
    def __init__(self, x, y, platform_width):
        # The enemy's visual size is larger than its hitbox for better aesthetics
        self.rect = pygame.Rect(x, y, TILE_SIZE * 1.5, TILE_SIZE * 1.5)
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2
        self.platform_width = platform_width
        self.start_x = x
        self.frames = enemy_frames
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 150 # milliseconds per frame

    def move(self):
        """Moves the enemy and reverses its direction at platform edges."""
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.start_x or self.rect.right >= self.start_x + self.platform_width:
            self.direction *= -1

    def update_animation(self, dt):
        """Updates the animation frame based on delta time."""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface, scroll_x, dt):
        """Updates animation and draws the enemy."""
        self.update_animation(dt)
        image = self.frames[self.frame_index]
        # Flip the image based on the direction the enemy is facing
        if self.direction == 1:
            image = pygame.transform.flip(image, True, False)
        # Adjust vertical position to align enemy's feet with the platform
        pos = (self.rect.x - scroll_x, self.rect.y + TILE_SIZE - image.get_height())
        surface.blit(image, pos)

class Part:
    """Represents a collectible part that the player needs to find."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = random.choice(part_images)
        self.float_direction = 1
        self.float_offset = 0
        self.float_speed = 0.5
        self.float_range = 5

    def update(self):
        """Updates the floating animation of the part."""
        self.float_offset += self.float_direction * self.float_speed
        if abs(self.float_offset) >= self.float_range:
            self.float_direction *= -1

    def draw(self, surface, scroll_x):
        """Draws the part on the screen."""
        pos = (self.rect.x - scroll_x, self.rect.y + self.float_offset)
        surface.blit(self.image, pos)

class Player:
    """Represents the player character."""
    def __init__(self, x, y):
        # Physics and state variables
        self.rect = pygame.Rect(x, y, TILE_SIZE * 0.8, TILE_SIZE) # Make hitbox slightly smaller than tile
        self.velocity = [0, 0]
        self.on_ground = False
        self.lives = 3
        self.collected_parts = 0
        self.spawn_point = (x, y)

        # Player attributes
        self.speed = 7
        self.jump_strength = 22
        self.gravity = 1.0
        self.max_fall_speed = 18

        # Invulnerability state after taking damage
        self.invulnerable = False
        self.invulnerable_duration = 2000 # in milliseconds
        self.invulnerable_timer = 0

        # Animation state machine
        self.state = "idle"
        self.animations = self.load_player_animations()
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100 # ms per frame
        self.facing_right = True
        self.hurt_timer = 0

        # Controller settings
        self.controller_deadzone = 0.2

    def load_player_animations(self):
        """Loads all player animation frames from image files."""
        animations = {}
        anim_data = {
            "win": ("assets/player/win/win.png", 92, 63),
            "idle": [f"assets/player/idle/idle-{i}.png" for i in range(1, 5)],
            "walk": [f"assets/player/walk/walk_{i}.png" for i in range(1, 11)],
            "fall": [f"assets/player/fall/fall-{i}.png" for i in range(1, 5)],
            "jump": ("assets/player/jump/jump.png", 86, 64),
            "lose": ("assets/player/lose/lose.png", 98, 64),
            "hurt": [f"assets/player/hurt/hurt_{i}.png" for i in range(1, 4)]
        }

        for state, data in anim_data.items():
            if isinstance(data, tuple): # Spritesheet
                sheet_path, frame_w, frame_h = data
                sheet = pygame.image.load(sheet_path).convert_alpha()
                animations[state] = self.split_spritesheet(sheet, frame_w, frame_h)
            else: # Individual frames
                animations[state] = [pygame.image.load(p).convert_alpha() for p in data]
        return animations

    def split_spritesheet(self, sheet, frame_width, frame_height):
        """Splits a spritesheet into a list of individual frame images."""
        frames = []
        sheet_width, _ = sheet.get_size()
        for i in range(sheet_width // frame_width):
            frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

    def update_animation(self, dt):
        """Updates the current animation frame based on delta time."""
        # For single-frame animations, no update is needed
        if len(self.animations[self.state]) <= 1:
            self.frame_index = 0
            return

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])

    def set_state(self):
        """Determines the player's animation state based on their actions."""
        # Hurt state takes priority
        if self.hurt_timer > 0:
            new_state = "hurt"
        # Then check for aerial states
        elif not self.on_ground:
            new_state = "jump" if self.velocity[1] < 0 else "fall"
        # Then ground states
        else:
            new_state = "walk" if abs(self.velocity[0]) > 0 else "idle"

        # If the state has changed, reset the animation
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0
            self.animation_timer = 0

    def draw(self, surface, scroll, dt):
        """Draws the player on the screen."""
        self.set_state()
        self.update_animation(dt)

        current_image = self.animations[self.state][self.frame_index]
        # Scale up the player sprite for a better visual size
        scaled_image = pygame.transform.scale(current_image, (current_image.get_width() * 2, current_image.get_height() * 2))

        # Flip the image if facing left
        if not self.facing_right:
            scaled_image = pygame.transform.flip(scaled_image, True, False)

        # Center the scaled image over the player's hitbox
        x = self.rect.x - scroll - (scaled_image.get_width() - self.rect.width) // 2
        y = self.rect.bottom - scaled_image.get_height()

        # Make player semi-transparent when invulnerable for visual feedback
        if self.invulnerable and (pygame.time.get_ticks() // 100) % 2 == 0:
            # This creates a blinking effect
            pass # Don't draw the player to make them "blink"
        else:
            surface.blit(scaled_image, (x, y))


    def move(self, keys, tiles, controller=None):
        """Handles player movement and input."""
        dx = 0
        
        # --- Horizontal Movement ---
        # Keyboard controls
        if keys[K_LEFT] or keys[K_a]:
            dx = -self.speed
            self.facing_right = False
        if keys[K_RIGHT] or keys[K_d]:
            dx = self.speed
            self.facing_right = True

        # Controller controls (analog stick)
        if controller:
            analog_x = controller.get_axis(0)
            if abs(analog_x) > self.controller_deadzone:
                dx = self.speed * analog_x
                if dx != 0: # Only change direction if there's movement
                    self.facing_right = analog_x > 0

        self.velocity[0] = dx

        # --- Vertical Movement (Jumping) ---
        # Keyboard jump
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.velocity[1] = -self.jump_strength
            self.on_ground = False
            if sound_on: jump_sound.play()

        # Controller jump (typically the 'A' button, which is button 0)
        if controller and controller.get_button(0) and self.on_ground:
            self.velocity[1] = -self.jump_strength
            self.on_ground = False
            if sound_on: jump_sound.play()

        # --- Apply Gravity ---
        self.velocity[1] += self.gravity
        # Clamp falling speed to prevent excessive velocity
        if self.velocity[1] > self.max_fall_speed:
            self.velocity[1] = self.max_fall_speed

        dy = self.velocity[1]

        # --- Collision Handling ---
        self.handle_collision(tiles, self.velocity[0], dy)
        self.check_on_ground(tiles)

    def handle_collision(self, tiles, dx, dy):
        """Handles collision with solid tiles."""
        # Move horizontally and check for collisions
        self.rect.x += dx
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                if dx > 0: # Moving right
                    self.rect.right = tile['rect'].left
                elif dx < 0: # Moving left
                    self.rect.left = tile['rect'].right

        # Move vertically and check for collisions
        self.rect.y += dy
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                if dy > 0: # Moving down
                    self.rect.bottom = tile['rect'].top
                    self.velocity[1] = 0
                    self.on_ground = True
                elif dy < 0: # Moving up
                    self.rect.top = tile['rect'].bottom
                    self.velocity[1] = 0

    def check_on_ground(self, tiles):
        """Checks if the player is standing on a solid tile."""
        # Temporarily move the player down 1 pixel to check for ground
        self.rect.y += 1
        on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile['rect']):
                on_ground = True
                break
        self.rect.y -= 1
        self.on_ground = on_ground

    def update_timers(self, dt):
        """Updates all time-based states for the player."""
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        if self.hurt_timer > 0:
            self.hurt_timer = max(0, self.hurt_timer - dt)

    def respawn(self):
        """Resets the player to their spawn point after losing a life."""
        self.rect.topleft = self.spawn_point
        self.velocity = [0, 0]
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration

    def take_damage(self):
        """Handles the logic for when the player takes damage."""
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            self.hurt_timer = 300 # Duration of the hurt animation
            if sound_on:
                hurt_sound.play()
            if self.lives <= 0:
                return "game_over"
        return "none"

# --- Game Functions ---

def parse_map(world_map):
    """Parses the string-based map into lists of game objects."""
    tiles, traps, parts, enemies = [], [], [], []
    goal = None
    
    for row_index, row in enumerate(world_map):
        platform_start = None
        for col_index, char in enumerate(row):
            x = col_index * TILE_SIZE
            y = SCREEN_HEIGHT - (len(world_map) - row_index) * TILE_SIZE
            
            if char == 'X':
                tiles.append({'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 'sprite': terrain_tileset})
                if platform_start is None:
                    platform_start = col_index
            elif char != 'X' and platform_start is not None:
                # End of a platform, check if an enemy should spawn
                platform_end = col_index
                platform_width_tiles = platform_end - platform_start
                
                # Check for 'N' (no-spawn) marker in the row above
                no_spawn = False
                if row_index > 0 and platform_width_tiles >= 4:
                    for i in range(platform_start, platform_end):
                        if world_map[row_index - 1][i] == 'N':
                            no_spawn = True
                            break
                
                if not no_spawn and platform_width_tiles >= 4:
                    enemy_x = platform_start * TILE_SIZE
                    enemy_y = y - TILE_SIZE
                    enemies.append(Enemy(enemy_x, enemy_y, platform_width_tiles * TILE_SIZE))

                platform_start = None

            elif char == 't':
                traps.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif char == 's':
                parts.append(Part(x, y))
            elif char == 'G':
                goal = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            elif char == 'P':
                player_start_pos = (x, y)

    return tiles, traps, parts, goal, enemies, player_start_pos

def draw_intro_screen():
    """Draws the main menu/intro screen and its buttons."""
    screen.blit(intro_bg, (0, 0))

    # Draw title with a shadow for better visibility
    shadow_offset = 4
    title_text = "The Mysterious Path"
    shadow = title_font.render(title_text, True, (0, 0, 0, 128))
    screen.blit(shadow, (SCREEN_WIDTH // 2 - shadow.get_width() // 2 + shadow_offset, SCREEN_HEIGHT // 4 - shadow.get_height() // 2 + shadow_offset))
    title = title_font.render(title_text, True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4 - title.get_height() // 2))

    # Button layout
    button_width, button_height, button_spacing = 300, 60, 20
    start_x = SCREEN_WIDTH // 2 - button_width // 2
    start_y = SCREEN_HEIGHT // 2

    # Create buttons
    start_button = Button("Start Game", start_x, start_y, button_width, button_height, (0, 100, 0), WHITE, (0, 150, 0), font)
    
    music_text = "Music: ON" if music_on else "Music: OFF"
    music_button = Button(music_text, start_x, start_y + (button_height + button_spacing), button_width, button_height, (100, 180, 255), BLACK, (150, 200, 255), font)
    
    sound_text = "Sound FX: ON" if sound_on else "Sound FX: OFF"
    sound_button = Button(sound_text, start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height, (100, 180, 255), BLACK, (150, 200, 255), font)
    
    controls_button = Button("Controls", start_x, start_y + 3 * (button_height + button_spacing), button_width, button_height, (100, 180, 255), BLACK, (150, 200, 255), font)

    buttons = [start_button, music_button, sound_button, controls_button]
    
    # Check for hover and draw buttons
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)

    pygame.display.flip()
    return buttons

def draw_text_screen(text, duration_ms=2000):
    """Displays a centered message on a black screen for a set duration."""
    screen.fill(BLACK)
    message = large_font.render(text, True, WHITE)
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(duration_ms) # Simple wait, fine for transitions

def draw_message(text, color=WHITE):
    """Draws a message overlay on the game screen, typically a hint."""
    message = font.render(text, True, color)
    # Position message above the center
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    # Add a semi-transparent background for readability
    bg_rect = message_rect.inflate(20, 20)
    s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, bg_rect)
    screen.blit(message, message_rect)

def reset_game_state(level_index):
    """Resets the game to the start of a specific level."""
    tiles, traps, parts, goal, enemies, player_pos = parse_map(world_maps[level_index])
    player = Player(player_pos[0], player_pos[1])
    return player, tiles, traps, parts, goal, enemies

def play_final_challenge():
    """A simple reaction-based mini-game for the end."""
    number = random.randint(0, 9)
    prompt_text = f"Press the number {number} to fix the plane!"
    
    start_time = pygame.time.get_ticks()
    time_limit = 3000 # 3 seconds

    while pygame.time.get_ticks() - start_time < time_limit:
        # Draw the prompt on every frame
        screen.fill(WHITE)
        text_surface = large_font.render(prompt_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.unicode == str(number):
                    return True # Success
        clock.tick(FPS)
    return False # Failed

def draw_background(scroll):
    """Draws the parallax scrolling background."""
    for i, bg in enumerate(bg_images):
        # Each layer scrolls at a different speed to create depth
        speed = 0.2 * (i + 1)
        # The modulo operator creates a seamless loop
        offset = int(-(scroll * speed)) % SCREEN_WIDTH
        screen.blit(bg, (offset - SCREEN_WIDTH, 0))
        screen.blit(bg, (offset, 0))

def draw_hud(surface, lives, collected_parts, current_level_num):
    """Draws the Heads-Up Display (lives, parts, level)."""
    # Draw lives
    for i in range(lives):
        surface.blit(life_image, (10 + i * (life_image.get_width() + 5), 10))
    
    # Draw collected parts text
    parts_text = font.render(f"Parts: {collected_parts}/3", True, WHITE)
    surface.blit(parts_text, (10, 50))
    
    # Draw current level text
    level_text = font.render(f"Level: {current_level_num}", True, WHITE)
    surface.blit(level_text, (10, 90))

def draw_controls_screen():
    """Displays the controls screen."""
    showing_controls = True
    while showing_controls:
        screen.fill(BLACK)
        controls = [
            "=== Keyboard ===",
            "A/D or Left/Right Arrows - Move",
            "W, Up Arrow, or Space - Jump",
            "E - Interact",
            "",
            "=== Controller ===",
            "Left Stick - Move",
            "A Button (Bottom Face) - Jump",
            "X Button (Left Face) - Interact",
            "",
            "Press ESC to return to menu"
        ]
        
        y_offset = SCREEN_HEIGHT // 4
        for line in controls:
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 50
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                showing_controls = False
        
        clock.tick(FPS)

# --- Main Game Loop ---

def main():
    """The main function that runs the game."""
    global sound_on, music_on
    
    game_state = "intro"
    current_level_index = 0
    player, tiles, traps, parts, goal, enemies = reset_game_state(current_level_index)

    # Timers for sound effects
    last_footstep_time = 0
    footstep_delay = 300 # ms

    running = True
    scroll = 0
    
    while running:
        # Delta time for frame-rate independent physics and animations
        dt = clock.tick(FPS)
        
        # Get the primary controller if one is connected
        controller = controllers[0] if controllers else None

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            # Handle intro screen button clicks
            if game_state == "intro" and event.type == MOUSEBUTTONDOWN:
                buttons = draw_intro_screen() # Get current buttons
                start_button, music_button, sound_button, controls_button = buttons
                
                if start_button.is_clicked(event.pos):
                    game_state = "playing"
                    if music_on:
                        try:
                            pygame.mixer.music.load("assets/music/glasba_ozadje.mp3")
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print(f"Could not load main game music: {e}")

                elif music_button.is_clicked(event.pos):
                    music_on = not music_on
                    if music_on: pygame.mixer.music.unpause()
                    else: pygame.mixer.music.pause()

                elif sound_button.is_clicked(event.pos):
                    sound_on = not sound_on
                
                elif controls_button.is_clicked(event.pos):
                    draw_controls_screen()

            # Handle interaction key press (E or Controller X)
            is_interaction_press = (event.type == KEYDOWN and event.key == K_e) or \
                                   (controller and event.type == JOYBUTTONDOWN and event.button == 2)

            if game_state == "playing" and is_interaction_press:
                if goal and player.rect.colliderect(goal) and player.collected_parts >= 3:
                    if current_level_index < len(world_maps) - 1:
                        # Move to the next level
                        current_level_index += 1
                        player, tiles, traps, parts, goal, enemies = reset_game_state(current_level_index)
                        scroll = 0 # Reset scroll for new level
                    else:
                        # Final level completed, start the mini-game
                        if play_final_challenge():
                            game_state = "game_complete"
                        else:
                            draw_text_screen("Repair failed! The apes caught you!", 2000)
                            game_state = "game_over"

        # --- Game State Logic ---
        if game_state == "intro":
            draw_intro_screen()

        elif game_state == "playing":
            # --- Update Game Objects ---
            keys = pygame.key.get_pressed()
            player.move(keys, tiles, controller)
            player.update_timers(dt)

            for enemy in enemies:
                enemy.move()
            for part in parts:
                part.update()

            # --- Handle Collisions and Events ---
            # Check for falling out of the world
            if player.rect.top > SCREEN_HEIGHT:
                player.lives -= 1
                if player.lives > 0:
                    player.respawn()
                else:
                    game_state = "game_over"

            # Check for collision with enemies
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    if player.take_damage() == "game_over":
                        game_state = "game_over"
            
            # Check for collision with parts
            for part_obj in parts[:]:
                if player.rect.colliderect(part_obj.rect):
                    parts.remove(part_obj)
                    player.collected_parts += 1
                    if sound_on: parts_sound.play()

            # --- Scrolling ---
            # Smooth camera scrolling that follows the player
            desired_scroll = player.rect.centerx - SCREEN_WIDTH // 2
            scroll += (desired_scroll - scroll) * 0.1 # The 0.1 creates a smooth "lerp" effect
            # Clamp scroll to level boundaries
            level_width = len(world_maps[current_level_index][0]) * TILE_SIZE
            scroll = max(0, min(scroll, level_width - SCREEN_WIDTH))

            # --- Drawing ---
            draw_background(scroll)

            for tile in tiles:
                screen.blit(tile['sprite'], (tile['rect'].x - scroll, tile['rect'].y))
            
            for enemy in enemies:
                enemy.draw(screen, scroll, dt)
            
            for part_obj in parts:
                part_obj.draw(screen, scroll)
            
            if goal:
                goal_pos = (goal.x - scroll - TILE_SIZE * 0.25, goal.y - goal_image.get_height() + TILE_SIZE)
                screen.blit(goal_image, goal_pos)
            
            player.draw(screen, scroll, dt)
            
            draw_hud(screen, player.lives, player.collected_parts, current_level_index + 1)
            
            # Display interaction prompts
            if goal and player.rect.colliderect(goal):
                if player.collected_parts >= 3:
                    if current_level_index < len(world_maps) - 1:
                        draw_message(f"Press E to proceed to Level {current_level_index + 2}!")
                    else:
                        draw_message("Press E for the final challenge!")
                else:
                    draw_message("You need to collect all the parts first!")

        elif game_state == "game_over":
            draw_text_screen("Game Over!")
            # Reset for a new game
            current_level_index = 0
            player, tiles, traps, parts, goal, enemies = reset_game_state(current_level_index)
            game_state = "intro"
            if music_on:
                pygame.mixer.music.load("assets/music/intro.ogg")
                pygame.mixer.music.play(-1)

        elif game_state == "game_complete":
            draw_text_screen("Congratulations! You've escaped!")
            # Reset for a new game
            current_level_index = 0
            player, tiles, traps, parts, goal, enemies = reset_game_state(current_level_index)
            game_state = "intro"
            if music_on:
                pygame.mixer.music.load("assets/music/intro.ogg")
                pygame.mixer.music.play(-1)

        # Update the full display Surface to the screen
        pygame.display.flip()

    # --- Shutdown ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
