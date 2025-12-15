import pygame

from scripts.game_manager import GM
from scripts.tileset import Tile


class Player(pygame.sprite.Sprite):
    COLOUR_GREEN = (0, 200, 0, 255)
    COLOUR_RED = (200, 0, 0, 255)

    def __init__(self, tile_map_loader):
        super().__init__()
        self.tile_map_loader = tile_map_loader

        # --- Sprite Setup ---
        self.image = self.tile_map_loader.get_tile(Tile.PLAYER_CHARACTER.value)
        self.rect = self.image.get_rect()

        self.selector = self.tile_map_loader.get_tile(Tile.SELECTOR.value)
        self.selector_rect = self.selector.get_rect()

        self.facing_dir = (0, 0)  # (dx, dy) vector for targeting/movement

        # --- Positioning ---
        self.rect.centerx = GM.screen_width // 2
        self.rect.centery = GM.screen_height // 2

        # --- Game Grid State  ---
        self.grid_x = 0
        self.grid_y = 0

        # --- Visual Animation State ---
        # These properties will be animated by EntityActions.move_entity
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)

        self.is_moving = False

    def get_grid_pos(self):
        """Returns the player's position in the map grid."""
        return self.grid_x, self.grid_y

    def set_grid_pos(self, x, y):
        """Sets the player's starting position in the map grid."""
        self.grid_x = x
        self.grid_y = y
        if not self.is_moving:
            self.sync_visual_offset()

    def sync_visual_offset(self):
        """
        Ensures the visual offset is set to the current logical grid position.
        Called on startup or after a non-animated teleport.
        """
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)

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
            if target_tile_index in Tile.get_enemy_tiles():
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
        dx, dy = self.facing_dir

        if (dx, dy) == (0, 0):
            return False

        # --- Calculate Target Position ---
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        target_tile_index = GM.current_level.get_tile_at(new_x, new_y)

        # --- Check for INTERACTION (Door/Chest) or ATTACK (Enemy) ---
        if target_tile_index in Tile.get_enemy_tiles() or target_tile_index in Tile.get_selectable_tiles():

            animation_info = GM.current_level.process_action(new_x, new_y, target_tile_index)

            if animation_info:
                # Interaction succeeded (e.g., door animation started)
                print(f"Player initiated action on tile ID {target_tile_index}.")
                self.facing_dir = (0, 0)
                # Returns the (x, y, final_id) tuple from Level.process_action
                return animation_info
            else:
                # Action failed
                return False

        # --- Check for MOVEMENT ---
        if target_tile_index in Tile.get_walkable_tiles():

            # --- Successful Move ---
            print(f"Player moved to ({new_x}, {new_y}).")

            from scripts.entity_actions import EntityActions
            entity_actions = EntityActions()
            entity_actions.move_player(self, new_x, new_y, duration_frames=12)
            entity_actions.move_entity(self, new_x, new_y, duration_frames=12)
            self.facing_dir = (0, 0)

            return True

            # --- Handle Blocked Actions ---
        else:
            print(f"Action blocked: Tile ID {target_tile_index} cannot be targeted.")
            return False

    def update(self):
        """
        Calculates the sprite's visual slide during movement animation and updates its rect.
        The player is drawn at the screen center PLUS the visual slide offset.
        """

        center_x = GM.screen_width // 2
        center_y = GM.screen_height // 2

        slide_offset_x = (self.offset_x_visual - self.grid_x) * GM.render_tile_size
        slide_offset_y = (self.offset_y_visual - self.grid_y) * GM.render_tile_size

        self.rect.centerx = center_x + round(slide_offset_x)
        self.rect.centery = center_y + round(slide_offset_y)
