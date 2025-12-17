# main.py - Updated version
from sys import exit

import pygame

from scripts.GameStateMachine import GameState
from scripts.HUD_display import HUD_Manager
from scripts.entityClasses.death_cloud_emitter import DeathCloudEmitter
from scripts.entityClasses.player import Player
from scripts.game_manager import GM
from scripts.level import Level, levels
from scripts.support import SpriteSheet

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

# --- Initialize State Machine ---
state_machine = GameState()
GM.state_machine = state_machine

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


# --- Helper function to handle player input ---
def handle_player_input(event):
    """Handle player input based on game state."""
    current_state = state_machine.current_state.id

    if current_state == "player_turn":
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
                if action_success:
                    # Trigger state transition
                    GM.player_perform_action()

    # Handle pause for all states
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        if current_state in ["player_turn", "enemy_turn", "animating"]:
            state_machine.pause_game()
        elif current_state == "pause_screen":
            state_machine.unpause_game()


# --- Game Loop ---
while True:
    # Handle events based on current state
    current_state = state_machine.current_state.id
    if current_state == "start_screen":
        # Draw start screen and wait for input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    state_machine.start_game()

        # Draw start screen
        screen.fill((0, 0, 50))
        # Add your start screen drawing code here

    elif current_state == "player_turn":
        if not GM.is_locked:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()

                    exit()

                handle_player_input(event)

        # Update HUD and player

        GM.hud_manager.update()

        player_group.update()
    elif current_state == "player_animating":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state_machine.pause_game()

        GM.hud_manager.update()
        GM.resolve_animations()
    elif current_state == "enemy_turn":
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state_machine.pause_game()

        GM.hud_manager.update()
    elif current_state == "enemy_animating":
        # Enemy animations are playing
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state_machine.pause_game()
        # Update HUD during enemy animations
        GM.hud_manager.update()
        # Resolve animations (this will trigger state transition when done)
        GM.resolve_animations()
    elif current_state == "pause_screen":
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    state_machine.unpause_game()

        GM.hud_manager.update()
    elif current_state == "start_screen":
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    GM.hud_manager.reset()
                    state_machine.start_game()

    elif current_state == "game_over":
        # Game over screen - don't update HUD
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                exit()

        # Draw game over screen
        screen.fill((50, 0, 0))
        # Add your game over drawing code here

    # --- Drawing (for states that need game rendering) ---
    if current_state in ["player_turn", "player_animating", "enemy_turn", "enemy_animating", "pause_screen"]:
        screen.fill(BG_COLOR)

        # Draw Level
        GM.current_level.draw(screen)

        # Draw Player
        player_group.draw(screen)

        # Draw Selector (only in player_turn state)
        if current_state == "player_turn":
            GM.player.draw_selector(screen)

        # Draw effects
        GM.death_cloud.update_and_draw(screen)

        # Draw HUD
        GM.hud_manager.draw(screen)

        # Draw pause overlay if in pause screen
        if current_state == "pause_screen":
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            pause_surface.set_alpha(128)
            pause_surface.fill((0, 0, 0))
            screen.blit(pause_surface, (0, 0))

    elif current_state == "start_screen":
        # Draw start screen without HUD
        screen.fill((0, 0, 50))
        # Add your start screen drawing code here

    elif current_state == "game_over":
        # Draw game over screen without HUD
        screen.fill((50, 0, 0))
        # Add your game over drawing code here

    # --- Update Display ---
    pygame.display.update()
    clock.tick(60)
