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
def handle_movement_phase_input(event):
    """Handle player input during movement phase."""
    if event.type == pygame.KEYDOWN:
        # --- Move cursor with arrow keys ---
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            GM.player.move_cursor(0, -1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            GM.player.move_cursor(0, 1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            GM.player.move_cursor(-1, 0)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            GM.player.move_cursor(1, 0)

        # --- Confirm movement with ENTER or SPACE ---
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            success = GM.player.confirm_movement()
            # The confirm_movement method now handles state transitions internally
            # No need for additional state transitions here


def handle_action_phase_input(event):
    """Handle player input during action phase."""
    if event.type == pygame.KEYDOWN:
        # --- Set facing direction with arrow keys ---
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            GM.player.set_facing_direction(0, -1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            GM.player.set_facing_direction(0, 1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            GM.player.set_facing_direction(-1, 0)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            GM.player.set_facing_direction(1, 0)

        # --- Confirm action with ENTER or SPACE ---
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            GM.player.perform_action()
            # The perform_action method will trigger animations
            # State transition will happen when animations complete


# --- Game Loop ---
while True:
    # Handle events based on current state
    current_state = state_machine.current_state.id

    # Handle animations if they're running
    if GM.has_animations():
        GM.resolve_animations()
        GM.hud_manager.update()

        # Check if animations are done and we need to transition states
        if not GM.has_animations():
            if current_state == "player_movement_phase":
                # Movement animations complete, move to action phase
                # This should already be handled by the callback in confirm_movement
                pass
            elif current_state == "player_action_phase":
                # Action animations complete, move to enemy turn
                state_machine.player_action_complete()

    if current_state == "start_screen":
        # Draw start screen and wait for input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    state_machine.start_game()
                    GM.player.start_movement_phase()

        # Draw start screen
        screen.fill((0, 0, 50))

    elif current_state == "player_movement_phase":
        # Only process input if no animations are running
        if not GM.has_animations():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state_machine.pause_game()
                else:
                    handle_movement_phase_input(event)

        GM.hud_manager.update()
        player_group.update()

    elif current_state == "player_action_phase":
        # Only process input if no animations are running
        if not GM.has_animations():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state_machine.pause_game()
                else:
                    handle_action_phase_input(event)

        GM.hud_manager.update()
        player_group.update()

    elif current_state == "enemy_turn":
        # We now use state_machine.enemy_turn_processed (defined in __init__)

        if not state_machine.enemy_turn_processed:
            print("[STATE] Processing enemy actions")

            # Reset which enemies have taken turns
            GM.current_level.reset_enemy_turn_tracking()

            enemy_actions_taken = GM.current_level.execute_enemy_turns()
            state_machine.enemy_turn_processed = True

            # If no actions were taken, transition immediately
            if not enemy_actions_taken:
                print("[STATE] No enemy actions, moving to player turn")
                state_machine.enemy_turn_complete()
                GM.player.start_movement_phase()
                state_machine.enemy_turn_processed = False

        # Check if animations are done
        if state_machine.enemy_turn_processed and not GM.has_animations():
            print("[STATE] Enemy animations complete, moving to player turn")
            state_machine.enemy_turn_complete()
            GM.player.start_movement_phase()
            state_machine.enemy_turn_processed = False

        GM.hud_manager.update()

    elif current_state == "pause_screen":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state_machine.unpause_game()

        GM.hud_manager.update()

    elif current_state == "game_over":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((50, 0, 0))

    # --- Drawing ---
    if current_state in ["player_movement_phase", "player_action_phase", "enemy_turn", "pause_screen"]:
        screen.fill(BG_COLOR)

        # Draw Level
        GM.current_level.draw(screen)

        # Draw movement range and cursor (only in movement phase)
        if current_state == "player_movement_phase" and not GM.has_animations():
            GM.player.draw_movement_range(screen)
            GM.player.draw_movement_cursor(screen)

        # Draw action selector (only in action phase)
        if current_state == "player_action_phase" and not GM.has_animations():
            GM.player.draw_action_selector(screen)

        # Draw Player
        player_group.draw(screen)

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
        screen.fill((0, 0, 50))

    elif current_state == "game_over":
        screen.fill((50, 0, 0))

    # --- Update Display ---
    pygame.display.update()
    clock.tick(60)

"""TODO: 
fix moving multiple squares animation (each tile should be 1 animation) 

improve move phase grid effect by having it grow out from the player when the phase starts,
    have it blit all tiles to one surface to draw, 
    add an outline effect in a slightly darker colour
    
POTENTIALLY: highlight interactables in range in green and 
             attackables in range in red and allow the player to spend their whole turn at once
             calculate how many moves player uses, move_speed should be a per turn variable not just the range

rework attack targeting to use facing_dir to choose direction of attack 
use 1x1 if no equipment 
add equipment have 
equipment change targetting options (ie. one attacks 3 squares away but not any closer, one attacks like a knight)

Add menu screens
"""
