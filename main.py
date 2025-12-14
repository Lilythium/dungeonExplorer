from sys import exit

import pygame

# --- Game Manager Integration ---
# Assume game_manager.py exists and defines the global GM instance
from game_manager import GM

from level import Level, levels
from sprites import SpriteSheet
from player import Player

# --- Constants ---
TILE_SIZE = 16
SCALING_FACTOR = 2
RENDER_TILE_SIZE = TILE_SIZE * SCALING_FACTOR

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 608
BG_COLOR = (20, 20, 30)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Dungeon Explorer')
clock = pygame.time.Clock()

# --- POPULATE GLOBAL MANAGER ---
GM.render_tile_size = RENDER_TILE_SIZE
GM.screen_width = SCREEN_WIDTH
GM.screen_height = SCREEN_HEIGHT

# --- SPRITE SETUP ---
TILE_MAP_LOADER = SpriteSheet("graphics/tilemap_packed.png", TILE_SIZE, TILE_SIZE, SCALING_FACTOR)

# --- PLAYER & LEVEL SETUP ---

# Instantiate Level and store it in GM
GM.current_level = Level(
    levels['test'],
    TILE_MAP_LOADER
)

# Instantiate Player and store it in GM
GM.player = Player(TILE_MAP_LOADER)
GM.player.set_grid_pos(8, 6)  # Initial player position

# Create the sprite group using the GM's player instance
player_group = pygame.sprite.GroupSingle(GM.player)

# --- Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            # --- Handle Targeting/Facing Direction ---
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                dx, dy = 0, -1
                GM.player.facing_dir = (dx, dy)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                dx, dy = 0, 1
                GM.player.facing_dir = (dx, dy)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                dx, dy = -1, 0
                GM.player.facing_dir = (dx, dy)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                dx, dy = 1, 0
                GM.player.facing_dir = (dx, dy)

            # --- Handle Movement ---
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if GM.player.perform_queued_action():
                    GM.handle_turn()

    # --- Drawing ---
    screen.fill(BG_COLOR)

    # Use GM.player to calculate offset
    player_pixel_x = GM.player.grid_x * GM.render_tile_size
    player_pixel_y = GM.player.grid_y * GM.render_tile_size

    # The offset calculation remains correct for centering
    offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
    offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

    # Draw Level
    GM.current_level.draw(screen, offset_x, offset_y)

    # Draw Player
    player_group.draw(screen)

    # Draw Selector (This uses the facing_dir set above)
    GM.player.draw_selector(screen)

    # --- Update ---
    pygame.display.update()
    clock.tick(60)
