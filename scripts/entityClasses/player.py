import pygame

from scripts.entityClasses.entity import Entity
from scripts.entity_actions import move_player
from scripts.game_manager import GM
from scripts.tileset import Tile


class Player(Entity):
    COLOUR_GREEN = (0, 200, 0, 255)
    COLOUR_RED = (200, 0, 0, 255)

    def __init__(self, tile_map_loader):
        super().__init__(tile_map_loader)
        self.tile_map_loader = tile_map_loader

        # --- Sprite Setup ---
        self.image = self.tile_map_loader.get_tile(Tile.PLAYER_CHARACTER.value)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()

        self.selector = self.tile_map_loader.get_tile(Tile.SELECTOR.value)
        self.selector_rect = self.selector.get_rect()

        self.facing_dir = (0, 0)  # (dx, dy) vector for targeting/movement

        # --- Positioning ---
        self.rect.centerx = GM.screen_width // 2
        self.rect.centery = GM.screen_height // 2

        # --- Visual Animation State ---
        # These properties will be animated by EntityActions.move_entity
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)
        self.squash_x = 1.0
        self.squash_y = 1.0
        self.is_moving = False

        # --- Combat Stats ---
        self.attack_dmg = 1
        self.max_health = 3
        self.current_health = self.max_health

    def set_grid_pos(self, x, y):
        """Sets the player's starting position in the map grid."""
        self.grid_x = x
        self.grid_y = y
        self.offset_x_visual = float(x)
        self.offset_y_visual = float(y)

    def get_selector_position(self):
        """
        Calculates the grid and screen position of the target tile.
        """
        if self.facing_dir == (0, 0):
            return None

        current_x, current_y = self.get_grid_pos()
        dir_x, dir_y = self.facing_dir

        target_grid_x = current_x + dir_x
        target_grid_y = current_y + dir_y

        selector_screen_x = self.rect.x + (dir_x * GM.render_tile_size)
        selector_screen_y = self.rect.y + (dir_y * GM.render_tile_size)

        return target_grid_x, target_grid_y, selector_screen_x, selector_screen_y

    def get_colored_selector(self, colour):
        """Creates a temporary, colored version of the selector sprite."""
        # NOTE: its probably more efficient to just store these copies somewhere
        colored_selector = self.selector.copy()
        colored_selector.fill(colour, special_flags=pygame.BLEND_MULT)
        return colored_selector

    def draw_selector(self, surface):
        """
        Draws the selector sprite.
        """
        selector_info = self.get_selector_position()

        if selector_info:
            target_grid_x, target_grid_y, screen_x, screen_y = selector_info

            target_tile_index = GM.current_level.get_tile_at(target_grid_x, target_grid_y)
            if GM.current_level.get_enemy_at(target_grid_x, target_grid_y):
                surface.blit(self.get_colored_selector(self.COLOUR_RED), (screen_x, screen_y))
            elif target_tile_index in Tile.get_selectable_tiles():
                surface.blit(self.get_colored_selector(self.COLOUR_GREEN), (screen_x, screen_y))
            elif target_tile_index in Tile.get_walkable_tiles():
                surface.blit(self.selector, (screen_x, screen_y))

    def perform_queued_action(self):
        """
        Executes the queued action based on self.facing_dir.

        Returns:
            False: Action blocked (no turn consumed).
            True: Simple move action (triggers animation lock, no tile swap needed).
            tuple: (pos_x, pos_y, final_tile_id) if an interaction/attack needs cleanup.
        """
        from scripts.game_manager import GM  # Import at top of file if not already there

        dx, dy = self.facing_dir

        if (dx, dy) == (0, 0):
            return False

        # --- Calculate Target Position ---
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        target_tile_index = GM.current_level.get_tile_at(new_x, new_y)

        # --- Check for ATTACK ---
        attack_target = GM.current_level.get_enemy_at(new_x, new_y)
        if attack_target:
            self.attack_enemy(attack_target)
        # --- Check for INTERACTION (Door/Chest) ---
        if target_tile_index in Tile.get_selectable_tiles():

            animation_info = GM.current_level.process_action(new_x, new_y, target_tile_index)

            if animation_info:
                # Interaction succeeded (e.g., door animation started)
                print(f"Player initiated action on tile ID {target_tile_index}.")
                self.facing_dir = (0, 0)
                # Signal that enemy turns should process after animations
                GM.start_turn()
                return animation_info
            else:
                # Action failed
                return False

        # --- Check for MOVEMENT ---
        if target_tile_index in Tile.get_walkable_tiles():

            # --- Successful Move ---
            print(f"Player moved to ({new_x}, {new_y}).")

            move_player(self, new_x, new_y, duration_frames=10)
            self.is_moving = True
            if self.facing_dir[0] != 0:
                self.squash_y = 1.1
                self.squash_x = 0.9
            else:
                self.squash_x = 1.1
                self.squash_y = 0.9
            self.facing_dir = (0, 0)

            # Signal that enemy turns should process after animations
            GM.start_turn()
            return True

        # --- Handle Blocked Actions ---
        else:
            print(f"Action blocked: Tile ID {target_tile_index} cannot be targeted.")
            return False

    def attack_enemy(self, enemy):
        enemy.take_damage(self.attack_dmg, self.facing_dir)

    def take_damage(self, amount: int, direction: tuple[int, int]):
        self.current_health -= amount
        new_x, new_y = self.get_grid_pos()
        new_x += -direction[0]
        new_y += -direction[1]
        move_player(self, new_x, new_y, duration_frames=8)

        if self.current_health <= 0:
            self.game_over()

    def update(self):
        """
        Player stays centered - camera movement handles positioning.
        """
        center_x = GM.screen_width // 2
        center_y = GM.screen_height // 2

        # Apply squash & stretch if moving
        if self.is_moving and (self.squash_x != 1.0 or self.squash_y != 1.0):
            new_width = int(self.original_image.get_width() * self.squash_x)
            new_height = int(self.original_image.get_height() * self.squash_y)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        elif not self.is_moving:
            # Reset to original image when not moving
            self.image = self.original_image.copy()

        # Keep player centered
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x
        self.rect.centery = center_y

    def game_over(self):
        pass
