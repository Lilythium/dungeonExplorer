import pygame
from tileset import Tile
from game_manager import GM  # <--- ESSENTIAL: Import the global manager


class Player(pygame.sprite.Sprite):
    # FIX: Only need tile_map_loader, everything else comes from GM
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

        target_tile_index = GM.current_level.get_tile_at(target_grid_x, target_grid_y)

        if target_tile_index in Tile.get_walkable_tiles():  # change to get_selectable_tiles() later
            selector_screen_x = self.rect.x + (dir_x * GM.render_tile_size)
            selector_screen_y = self.rect.y + (dir_y * GM.render_tile_size)

            return target_grid_x, target_grid_y, selector_screen_x, selector_screen_y

        return None

    def draw_selector(self, surface):
        """
        Draws the selector sprite.
        """
        selector_info = self.get_selector_position()

        if selector_info:
            _, _, screen_x, screen_y = selector_info
            surface.blit(self.selector, (screen_x, screen_y))

    def update(self):
        """
        Since the player is always fixed in the center, this method
        might be used later for animation or input handling.
        """
        pass
