from sys import exit

import pygame

from scripts.entityClasses.death_cloud_emitter import DeathCloudEmitter
from scripts.entityClasses.player import Player
from scripts.game_manager import GM
from scripts.level import Level, levels
from scripts.support import SpriteSheet
from scripts.HUD_display import HUD_Manager

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
GM.player.set_grid_pos(10, 8)  # Initial player position
GM.player.sync_visual_offset()

# Set initial camera position to center on player
player_pixel_x = GM.player.grid_x * GM.render_tile_size
player_pixel_y = GM.player.grid_y * GM.render_tile_size
initial_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
initial_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)
GM.current_level.set_initial_camera_position(initial_offset_x, initial_offset_y)

player_group = pygame.sprite.GroupSingle(GM.player)
GM.hud_manager = HUD_Manager(TILE_MAP_LOADER)
GM.death_cloud = DeathCloudEmitter()
# --- Game Loop ---
while True:
    if GM.is_locked:
        GM.resolve_animations()
    else:
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

                # --- Handle Interactions ---
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    action_success = GM.player.perform_queued_action()

    # --- Update ---
    GM.hud_manager.update()
    player_group.update()
    # --- Drawing ---
    screen.fill(BG_COLOR)

    # Draw Level (it will use its own animated offset values)
    GM.current_level.draw(screen)

    # Draw Player
    player_group.draw(screen)

    # Draw Selector
    GM.player.draw_selector(screen)

    GM.death_cloud.update_and_draw(screen)
    GM.hud_manager.draw(screen)

    # --- Update ---
    pygame.display.update()
    clock.tick(60)

"""
TODO for 17th:
make taking damage actually affect the players health 
implement game states (start screen, level, game over screen)
"""