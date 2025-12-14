import pygame
from support import import_csv_layout
from tileset import Tile
from game_manager import GM


class Level:
    def __init__(self, level_data, tile_map_loader):

        self.tile_map_loader = tile_map_loader

        self.terrain_data = import_csv_layout(level_data['terrain'])

        self.level_surface = self.setup_level_surface()

        self.offset_x = 0
        self.offset_y = 0

    def setup_level_surface(self):
        """
        Creates a single, large Pygame Surface containing all terrain tiles.
        """
        if not self.terrain_data:
            return pygame.Surface((0, 0))  # Return empty if no data

        # Get tile dimensions from the first sprite loaded
        sample_sprite = self.tile_map_loader.get_tile(Tile.GROUND.value)
        tile_width = sample_sprite.get_width()
        tile_height = sample_sprite.get_height()

        # Determine the overall size of the map surface
        map_width = len(self.terrain_data[0]) * tile_width
        map_height = len(self.terrain_data) * tile_height

        # Create the large surface where the entire map will be drawn
        map_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        # Draw all tiles onto the new map_surface
        for row_index, row in enumerate(self.terrain_data):
            for col_index, tile_id_str in enumerate(row):

                tile_index = int(tile_id_str)

                if tile_index != Tile.EMPTY.value:
                    # Get the cached sprite (32x32)
                    sprite = self.tile_map_loader.get_tile(tile_index)

                    # Calculate the position within the large map_surface
                    x = col_index * tile_width
                    y = row_index * tile_height

                    # Blit the individual tile onto the large map_surface
                    map_surface.blit(sprite, (x, y))

        return map_surface

    def get_tile_at(self, pos_x, pos_y):
        """returns tile ID at x, y"""
        max_rows = len(self.terrain_data)
        max_cols = len(self.terrain_data[0]) if max_rows > 0 else 0

        # checks if valid coordinates
        if not (0 <= pos_x < max_cols):
            return Tile.EMPTY.value
        if not (0 <= pos_y < max_rows):
            return Tile.EMPTY.value

        return int(self.terrain_data[pos_y][pos_x])

    def draw(self, display_surface, offset_x=0, offset_y=0):
        """
        Draws the single, pre-rendered map surface to the display.
        Uses the provided offset for camera movement/scrolling.
        """
        self.offset_x = offset_x
        self.offset_y = offset_y

        display_surface.blit(self.level_surface, (offset_x, offset_y))


levels = {
    'test': {
        'terrain': 'data/testLevel.csv',
        # add other layers here later (e.g., 'enemies', 'props')
    }
}
