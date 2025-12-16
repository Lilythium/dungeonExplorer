import pygame

from scripts.entity_actions import move_entity
from .entity import Entity
from .player import Player
from ..game_manager import GM
from ..tileset import Tile


class Enemy(Entity):
    def __init__(self, tile_map_loader, spawn_x, spawn_y):
        super().__init__(tile_map_loader)

        # --- Essential Game References ---
        self.tile_map_loader = tile_map_loader  # Reference to the tile/sprite loading utility

        # --- Rendering and Pygame Setup ---
        self.image = self.tile_map_loader.get_tile(0)  # Placeholder, load actual enemy tile
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()  # Pygame rectangle for drawing/positioning

        # --- Logical Grid Position (Used for AI and turn-based logic) ---
        self.grid_x: int = spawn_x
        self.grid_y: int = spawn_y
        self.rect.topleft = (spawn_x * GM.render_tile_size, spawn_y * GM.render_tile_size)  # Initial screen position

        # --- Visual Animation State (Used by EntityActions.move_entity) ---
        # These track the fractional progress of the slide (0.0 to +/- 1.0)
        self.slide_x: float = 0.0
        self.slide_y: float = 0.0
        self.start_grid_x: int = self.grid_x  # The grid position before a move starts
        self.start_grid_y: int = self.grid_y
        self.is_moving: bool = False  # Flag to lock AI turns during animation

        # --- Squish ---
        self.squash_x: float = 1.0
        self.squash_y: float = 1.0

        # --- Combat and Stats ---
        self.max_hp: int = 1
        self.hit_points: int = 1
        self.is_alive: bool = True

        # --- AI and Behavior ---
        self.view_radius: int = 5  # How many tiles away the enemy can see the player
        self.ai_state: str = "PATROL"  # Current state (e.g., "PATROL", "CHASE", "ATTACK")
        self.patrol_route: list[tuple[int, int]] = []  # A list of (x, y) points to follow
        self.turn_timer: int = 0  # Optional delay/cooldown between actions
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

        # Determine step direction (always +1 or -1)
        step_x = 1 if player_x > current_x else -1
        step_y = 1 if player_y > current_y else -1

        # The algorithm will loop through the major axis (the larger distance)
        # to ensure it hits all tiles the line crosses.

        # Error accumulation variable
        err = dx - dy

        # Get the Level reference and blocking tiles list

        level = GM.current_level

        # Loop until we reach the player's tile
        while current_x != player_x or current_y != player_y:

            # --- Check the CURRENT tile (before stepping) ---
            # We don't check the enemy's starting tile, only the tiles in between.
            if current_x != self.grid_x or current_y != self.grid_y:
                tile_id = level.get_tile_at(current_x, current_y)
                walkable = Tile.get_walkable_tiles()
                selectable = Tile.get_selectable_tiles()
                enemies = Tile.get_enemy_tiles()
                if tile_id not in walkable and tile_id not in selectable and tile_id not in enemies:
                    # TODO: may want to create a set of tiles that do block vision
                    return False  # Vision is blocked

            # --- Step toward the player using the error term ---
            e2 = 2 * err

            if e2 > -dy:  # Move along the X axis
                err -= dy
                current_x += step_x

            if e2 < dx:  # Move along the Y axis
                err += dx
                current_y += step_y

        # If the loop finished without hitting a blocking tile, the path is clear.
        return True

    def take_turn(self, player_grid_pos: tuple[int, int]):
        """
        The main AI driver. Called during the enemy turn phase to decide the next action.
        """
        if self.is_moving:
            print(f"[ENEMY DEBUG] Enemy at {self.get_grid_pos()} is still moving")
            return False

        # State Transition Check
        if self.can_see_player(player_grid_pos):
            self.ai_state = "CHASE"
        elif self.ai_state == "CHASE":
            self.ai_state = "PATROL"

        # Execute Action Based on State
        action_taken = False
        match self.ai_state:
            case "CHASE":
                action_taken = self._do_chase(player_grid_pos)
                # If an action was queued, execute it
                if action_taken:
                    action_taken = self.perform_queued_action()
            case "PATROL":
                action_taken = self._do_patrol()
                if action_taken:
                    action_taken = self.perform_queued_action()
            case "ATTACK":
                # ATTACK state should be set by _do_chase if adjacent
                action_taken = self.perform_queued_action()

        return action_taken

    def _do_chase(self, player_grid_pos: tuple[int, int]) -> bool:
        """
        Calculates the best move to close the distance to the player and sets facing_dir.
        Returns True if a move/attack was successfully queued.
        """
        player_x, player_y = player_grid_pos
        enemy_x, enemy_y = self.grid_x, self.grid_y

        # Determine the difference
        dx = player_x - enemy_x
        dy = player_y - enemy_y

        # Check if the player is adjacent (ready for attack)
        if abs(dx) <= 1 and abs(dy) <= 1 and (abs(dx) + abs(dy)) > 0:
            # Player is adjacent - Queue the attack
            self.ai_state = "ATTACK"
            # Set facing_dir to the player's position for perform_queued_action to reference
            self.facing_dir = (player_x, player_y)
            return True  # Action queued

        # Player is not adjacent - Queue a move

        # Calculate the direction of the single best step
        target_x, target_y = enemy_x, enemy_y

        if abs(dx) >= abs(dy):
            # Move along the X axis if it closes the distance
            target_x += (1 if dx > 0 else -1)
        else:
            # Otherwise, move along the Y axis
            target_y += (1 if dy > 0 else -1)

        # Check if the calculated target is walkable
        if GM.current_level.is_walkable(target_x, target_y):
            self.facing_dir = (target_x, target_y)
            return True  # Move queued

        return False  # No action taken (e.g., path blocked)

    def _do_patrol(self) -> bool:
        """
        Follows the predefined patrol_route.
        """
        if not self.patrol_route:
            return False

        # --- 1. Check if we reached the current target point ---
        next_x, next_y = self.patrol_route[0]

        if self.grid_x == next_x and self.grid_y == next_y:
            # We reached the point: Rotate the patrol route
            self.patrol_route.append(self.patrol_route.pop(0))
            next_x, next_y = self.patrol_route[0]  # New target

        # --- 2. Calculate the single step towards the new target ---
        dx = next_x - self.grid_x
        dy = next_y - self.grid_y

        step_x = 0
        step_y = 0

        if abs(dx) > 0:
            step_x = 1 if dx > 0 else -1
        elif abs(dy) > 0:
            step_y = 1 if dy > 0 else -1

        target_x = self.grid_x + step_x
        target_y = self.grid_y + step_y

        # --- 3. Check walkability and queue move ---
        if GM.current_level.is_walkable(target_x, target_y):
            self.facing_dir = (target_x, target_y)
            return True

        return False  # Cannot move, patrol blocked or finished

    def perform_queued_action(self):
        """
        Executes the queued action based on self.facing_dir.

        This function either starts an attack sequence or initiates an animated movement
        via the EntityActions system.
        """
        # Safety check: If already moving, prevent new action.
        if self.is_moving:
            return False

        target_x, target_y = self.facing_dir
        player = GM.player

        # --- Attack Check ---
        if (target_x, target_y) == player.get_grid_pos():
            self.attack_player(player)
            self.ai_state = "CHASE"
            return True  # Turn consumed

        # --- Move Check and Execution ---
        if GM.current_level.is_walkable(target_x, target_y):
            # check move direction for squash
            if target_x - self.grid_y != 0:
                self.squash_y = 1.1
                self.squash_x = 0.9
            else:
                self.squash_x = 1.1
                self.squash_y = 0.9
            move_entity(self, target_x, target_y)
            # The logical position update (self.set_grid_pos) happens inside the
            # animation's on_complete_callback, NOT here.
            return True

        return False

    def attack_player(self, player_entity: Player):
        """
        Initiates a combat sequence against the player.
        """

        damage = 1
        origin_x, origin_y = self.get_grid_pos()
        destination_x, destination_y = player_entity.get_grid_pos()
        attack_dir = (origin_x - destination_x, origin_y - destination_y)
        # Apply damage to the player
        player_entity.take_damage(damage, attack_dir)

        # Trigger attack animation/sound effects/hit feedback
        # GM.event_system.trigger_feedback("ATTACK", self, player_entity)

    def take_damage(self, amount: int, direction: tuple[int, int]):
        """
        Processes incoming damage and updates health.
        """
        final_damage = amount

        self.hit_points -= final_damage

        new_x, new_y = self.get_grid_pos()
        new_x += direction[0]
        new_y += direction[1]
        move_entity(self, new_x, new_y, duration_frames=8)

        # Trigger visual feedback (e.g., color flash)

        if self.hit_points <= 0:
            self.die()

    def die(self):
        """
        Handles the enemy's death sequence and removal from the level.
        """
        self.is_alive = False
        self.kill()

    def update(self):
        """
        Calculates the enemy's pixel position based on the animated slide
        relative to the map's current draw position.
        """
        # Determine base position and slide offset
        if self.is_moving:
            base_grid_x = self.start_grid_x
            base_grid_y = self.start_grid_y
            slide_offset_x = self.slide_x * GM.render_tile_size
            slide_offset_y = self.slide_y * GM.render_tile_size

            # Apply squash & stretch while moving
            if self.squash_x != 1.0 or self.squash_y != 1.0:
                new_width = int(self.original_image.get_width() * self.squash_x)
                new_height = int(self.original_image.get_height() * self.squash_y)
                self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        else:
            base_grid_x = self.grid_x
            base_grid_y = self.grid_y
            slide_offset_x = 0
            slide_offset_y = 0

            # Reset to original image when not moving
            if self.squash_x != 1.0 or self.squash_y != 1.0:
                self.squash_x = 1.0
                self.squash_y = 1.0
                self.image = self.original_image.copy()

        # Calculate screen position using current camera offset
        screen_pos_x = (base_grid_x * GM.render_tile_size) + GM.current_level.offset_x
        screen_pos_y = (base_grid_y * GM.render_tile_size) + GM.current_level.offset_y

        # Add the slide offset
        self.rect.x = round(screen_pos_x + slide_offset_x)
        self.rect.y = round(screen_pos_y + slide_offset_y)
