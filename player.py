import pygame
from tileset import Tile
from game_manager import GM


class Player(pygame.sprite.Sprite):
    COLOUR_GREEN = (0, 200, 0, 255)
    COLOUR_RED = (200, 0, 0, 255)

    def __init__(self, tile_map_loader):
        super().__init__()
        self.tile_map_loader = tile_map_loader

        # --- Sprite Setup ---
        self.image = self.tile_map_loader.get_tile(Tile.PLAYER_CHARACTER.value)
        self.rect = self.image.get_rect()

        # FIX: Access the integer value for the SpriteSheet
        self.selector = self.tile_map_loader.get_tile(Tile.SELECTOR.value)
        self.selector_rect = self.selector.get_rect()

        self.facing_dir = (0, 0)  # (dx, dy) vector for targeting/movement

        # --- Positioning (Uses GM) ---
        # The Player is fixed to the center of the screen
        self.rect.centerx = GM.screen_width // 2
        self.rect.centery = GM.screen_height // 2

        # --- Game Grid State  ---
        self.grid_x = 0
        self.grid_y = 0

    def get_grid_pos(self):
        """Returns the player's position in the map grid."""
        return self.grid_x, self.grid_y

    def set_grid_pos(self, x, y):
        """Sets the player's starting position in the map grid."""
        self.grid_x = x
        self.grid_y = y

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
            print(target_tile_index)
            if target_tile_index in Tile.get_enemy_tiles():
                surface.blit(self.get_colored_selector(self.COLOUR_RED), (screen_x, screen_y))
            elif target_tile_index in Tile.get_selectable_tiles():
                print("Fountain found")
                surface.blit(self.get_colored_selector(self.COLOUR_GREEN), (screen_x, screen_y))
            elif target_tile_index in Tile.get_walkable_tiles():
                surface.blit(self.selector, (screen_x, screen_y))

    def perform_queued_action(self):
        """
        Executes the queued action based on self.facing_dir.
        If the action is a move, it updates the player's grid position
        after checking for collision against the current level terrain.

        Returns:
            bool: True if a move/action was successfully executed, False otherwise.
        """

        dx, dy = self.facing_dir

        if (dx, dy) == (0, 0):
            print("Action blocked: No direction selected.")
            return False

        # --- Calculate Target Position ---
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        target_tile_index = GM.current_level.get_tile_at(new_x, new_y)

        # TODO: check for enemies or other selectable tiles BEFORE walkable ones
        # Check for successful movement
        if target_tile_index in Tile.get_walkable_tiles():

            # --- Successful Move ---
            self.grid_x = new_x
            self.grid_y = new_y
            print(f"Player moved to ({self.grid_x}, {self.grid_y}).")

            # Reset facing_dir to clear the selector for the next turn
            self.facing_dir = (0, 0)

            return True

        # Handle blocked actions (e.g., walls, closed doors, out of bounds)
        else:
            print(f"Action blocked: Tile ID {target_tile_index} is not walkable.")
            return False

    def update(self):
        """
        Since the player is always fixed in the center, this method
        might be used later for animation or input handling.
        """
        pass
