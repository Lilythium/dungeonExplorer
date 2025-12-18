import random

import pygame

from scripts.entity_actions import move_entity
from scripts.pathfinding import get_next_step_towards
from .entity import Entity
from .player import Player
from ..game_manager import GM
from ..tileset import Tile


class Enemy(Entity):
    def __init__(self, tile_map_loader, spawn_x, spawn_y):
        super().__init__(tile_map_loader)

        # --- Essential Game References ---
        self.tile_map_loader = tile_map_loader

        # --- Movement Stats ---
        self.move_speed = 1  # Enemy moves 1 tile per turn

        # --- Rendering and Pygame Setup ---
        self.image = self.tile_map_loader.get_tile(0)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()

        # --- Logical Grid Position ---
        self.grid_x: int = spawn_x
        self.grid_y: int = spawn_y
        self.rect.topleft = (spawn_x * GM.render_tile_size, spawn_y * GM.render_tile_size)

        # --- Visual Animation State ---
        self.slide_x: float = 0.0
        self.slide_y: float = 0.0
        self.start_grid_x: int = self.grid_x
        self.start_grid_y: int = self.grid_y
        self.is_moving: bool = False

        # --- Squish ---
        self.squash_x: float = 1.0
        self.squash_y: float = 1.0

        # --- Combat and Stats ---
        self.max_health: int = 1
        self.current_health: int = 1
        self.is_alive: bool = True

        # --- AI and Behavior ---
        self.view_radius: int = 5
        self.ai_state: str = "PATROL"

        # Patrol waypoints - enemy will pathfind to each in order
        self.patrol_waypoints: list[tuple[int, int]] = []
        self.current_waypoint_index: int = 0

        self.turn_timer: int = 0
        self.facing_dir: tuple[int, int] = (0, 0)

    def can_see_player(self, player_grid_pos: tuple[int, int]) -> bool:
        """
        Checks if the player is within view_radius AND if there is a clear,
        non-blocking path (Line of Sight) using Bresenham's principle
        """
        player_x, player_y = player_grid_pos
        current_x, current_y = self.grid_x, self.grid_y

        # --- Check Distance ---
        dx = abs(player_x - current_x)
        dy = abs(player_y - current_y)
        distance = dx + dy

        if distance == 0:
            return False
        if distance > self.view_radius:
            return False

        # --- Line of Sight (LOS) ---
        step_x = 1 if player_x > current_x else -1
        step_y = 1 if player_y > current_y else -1

        err = dx - dy
        level = GM.current_level

        while current_x != player_x or current_y != player_y:
            # --- Check the CURRENT tile (before stepping) ---
            if current_x != self.grid_x or current_y != self.grid_y:
                tile_id = level.get_tile_at(current_x, current_y)
                walkable = Tile.get_walkable_tiles()
                selectable = Tile.get_selectable_tiles()
                if tile_id not in walkable and tile_id not in selectable and tile_id:
                    return False

            # --- Step toward the player using the error term ---
            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                current_x += step_x

            if e2 < dx:
                err += dx
                current_y += step_y

        return True

    def take_turn(self, player_grid_pos: tuple[int, int]):
        """
        The main AI driver. Called during the enemy turn phase to decide the next action.
        Returns True if an action was taken, False otherwise.
        """
        if not GM.state_machine or GM.state_machine.current_state.id != "enemy_turn":
            return False

        if self.is_moving:
            print(f"[ENEMY DEBUG] {self.__class__.__name__} at {self.get_grid_pos()} is still moving")
            return False

        # --- State Transition Check ---
        if self.can_see_player(player_grid_pos):
            self.ai_state = "CHASE"
        elif self.ai_state == "CHASE":
            self.ai_state = "PATROL"

        # --- Execute Action Based on State ---
        action_taken = False
        match self.ai_state:
            case "CHASE":
                action_taken = self._do_chase(player_grid_pos)
            case "PATROL":
                action_taken = self._do_patrol()
            case "ATTACK":
                action_taken = self._do_attack(player_grid_pos)

        return action_taken

    def _do_chase(self, player_grid_pos: tuple[int, int]) -> bool:
        """
        Moves towards the player using pathfinding.
        Returns True if a move/attack was successfully executed.
        """
        player_x, player_y = player_grid_pos
        enemy_x, enemy_y = self.grid_x, self.grid_y

        dx = player_x - enemy_x
        dy = player_y - enemy_y

        manhattan_distance = abs(dx) + abs(dy)
        is_cardinal_adjacent = manhattan_distance == 1

        if is_cardinal_adjacent:
            # --- Player is adjacent - Execute attack ---
            self.ai_state = "ATTACK"
            return self._do_attack(player_grid_pos)

        # --- Player is not adjacent - Move towards them ---
        next_step = get_next_step_towards(GM.current_level, enemy_x, enemy_y, player_x, player_y)

        if next_step:
            target_x, target_y = next_step

            # Check if destination is walkable
            if GM.current_level.is_walkable(target_x, target_y):
                # Determine squash direction
                if target_x - self.grid_x != 0:  # Horizontal movement
                    self.squash_y = 1.1
                    self.squash_x = 0.9
                else:  # Vertical movement
                    self.squash_x = 1.1
                    self.squash_y = 0.9

                move_entity(self, target_x, target_y)
                return True

        return False

    def _do_patrol(self) -> bool:
        """
        Follows the predefined patrol_waypoints using pathfinding.
        """
        if not self.patrol_waypoints:
            return False

        # --- Get current target waypoint ---
        target_x, target_y = self.patrol_waypoints[self.current_waypoint_index]

        # --- Check if we reached the current waypoint ---
        if self.grid_x == target_x and self.grid_y == target_y:
            # Move to next waypoint
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.patrol_waypoints)
            target_x, target_y = self.patrol_waypoints[self.current_waypoint_index]

        # --- Pathfind towards the waypoint ---
        next_step = get_next_step_towards(GM.current_level, self.grid_x, self.grid_y, target_x, target_y)

        if next_step:
            step_x, step_y = next_step

            if GM.current_level.is_walkable(step_x, step_y):
                # Determine squash direction
                if step_x - self.grid_x != 0:  # Horizontal movement
                    self.squash_y = 1.1
                    self.squash_x = 0.9
                else:  # Vertical movement
                    self.squash_x = 1.1
                    self.squash_y = 0.9

                move_entity(self, step_x, step_y)
                return True

        return False

    def _do_attack(self, player_grid_pos: tuple[int, int]) -> bool:
        """
        Executes the two-part attack animation: Lunge -> Damage -> Retreat.
        """
        if self.is_moving:
            return False

        target_x, target_y = player_grid_pos
        origin_x, origin_y = self.get_grid_pos()

        # --- Check attack direction for squash ---
        if target_x - self.grid_x != 0:  # Horizontal attack
            self.squash_x = 1.15
            self.squash_y = 0.85
        else:  # Vertical attack
            self.squash_y = 1.15
            self.squash_x = 0.85

        # --- LUNGE PHASE ---
        def lunge_complete_callback():
            self.attack_player(GM.player, origin_x, origin_y)

            # --- RETREAT PHASE ---
            retreat_x, retreat_y = origin_x, origin_y

            def retreat_complete_callback():
                self.is_moving = False
                self.set_grid_pos(origin_x, origin_y)
                self.ai_state = "CHASE"  # Reset to chase after attack

            move_entity(
                entity=self,
                target_grid_x=retreat_x,
                target_grid_y=retreat_y,
                duration_frames=10,
                on_complete_callback=retreat_complete_callback
            )

        move_entity(
            entity=self,
            target_grid_x=target_x,
            target_grid_y=target_y,
            duration_frames=4,
            on_complete_callback=lunge_complete_callback
        )

        self.is_moving = True
        return True

    def attack_player(self, player_entity: Player, origin_x, origin_y):
        """
        Initiates a combat sequence against the player.
        """
        damage = 1
        destination_x, destination_y = player_entity.get_grid_pos()
        attack_dir = (origin_x - destination_x, origin_y - destination_y)

        # --- Don't trigger state transition when player takes damage during enemy turn ---
        player_entity.take_damage(damage, attack_dir, suppress_state_transition=True)

    def take_damage(self, amount: int, direction: tuple[int, int]):
        """
        Processes incoming damage and updates health.
        """
        print(f"[ENEMY DEBUG] health: {self.current_health}/{self.max_health} taking {amount} dmg")
        self.current_health -= amount

        new_x, new_y = self.get_grid_pos()
        new_x += direction[0]
        new_y += direction[1]

        # --- Check if knockback destination is valid ---
        can_knockback = GM.current_level.is_walkable(new_x, new_y)

        # --- Ensure knockback completes before enemy can act again ---
        def on_knockback_complete():
            self.is_moving = False
            if self.current_health <= 0:
                self.die()

        # --- Only knockback if destination is walkable ---
        if can_knockback:
            print(f"[ENEMY DEBUG] Knocking back to ({new_x}, {new_y})")
            move_entity(self, new_x, new_y, duration_frames=8, on_complete_callback=on_knockback_complete)
        else:
            print(f"[ENEMY DEBUG] Knockback blocked, staying at ({self.grid_x}, {self.grid_y})")
            # --- Still need to set is_moving and handle death ---
            if self.current_health <= 0:
                self.die()

        self.start_damage_flash()

    def die(self):
        """
        Handles the enemy's death sequence and removal from the level.
        """
        if hasattr(GM, 'death_cloud') and GM.death_cloud:
            explosion_pos = self.rect.center
            particle_variation = random.randint(-3, 3)
            GM.death_cloud.burst(explosion_pos, num_particles=15 + particle_variation)

        self.is_alive = False
        self.kill()

    def update(self):
        """
        Calculates the enemy's pixel position based on the animated slide
        relative to the map's current draw position.
        """
        self.update_damage_flash()

        # --- Determine base position and slide offset ---
        if self.is_moving:
            base_grid_x = self.start_grid_x
            base_grid_y = self.start_grid_y
            slide_offset_x = self.slide_x * GM.render_tile_size
            slide_offset_y = self.slide_y * GM.render_tile_size

            # --- Apply squash & stretch while moving ---
            if self.squash_x != 1.0 or self.squash_y != 1.0:
                new_width = int(self.original_image.get_width() * self.squash_x)
                new_height = int(self.original_image.get_height() * self.squash_y)
                self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        else:
            base_grid_x = self.grid_x
            base_grid_y = self.grid_y
            slide_offset_x = 0
            slide_offset_y = 0

            # --- Reset to original image when not moving ---
            if self.squash_x != 1.0 or self.squash_y != 1.0:
                self.squash_x = 1.0
                self.squash_y = 1.0
                self.image = self.original_image.copy()

        # --- Calculate screen position using current camera offset ---
        screen_pos_x = (base_grid_x * GM.render_tile_size) + GM.current_level.offset_x
        screen_pos_y = (base_grid_y * GM.render_tile_size) + GM.current_level.offset_y

        # --- Add the slide offset ---
        self.rect.x = round(screen_pos_x + slide_offset_x)
        self.rect.y = round(screen_pos_y + slide_offset_y)
