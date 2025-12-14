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

    def set_tile_at(self, pos_x, pos_y, new_tile_id):
        """Sets the tile ID at the given grid coordinates."""
        max_rows = len(self.terrain_data)
        max_cols = len(self.terrain_data[0]) if max_rows > 0 else 0

        if 0 <= pos_x < max_cols and 0 <= pos_y < max_rows:
            # Update the stored map data (must be a string for consistency)
            self.terrain_data[pos_y][pos_x] = str(new_tile_id)

            # NOTE: For performance, a better solution is to only re-render the changed tile,
            # but re-rendering the whole map is simpler for now.
            self.level_surface = self.setup_level_surface()
            return True
        return False

    def draw(self, display_surface, offset_x=0, offset_y=0):
        """
        Draws the single, pre-rendered map surface to the display.
        Uses the provided offset for camera movement/scrolling.
        """
        self.offset_x = offset_x
        self.offset_y = offset_y

        display_surface.blit(self.level_surface, (offset_x, offset_y))

    # --- ACTIONS ---
    def _open_door_small(self, pos_x, pos_y):
        """
        Initiates the door opening sequence.

        Returns: Tuple (pos_x, pos_y, final_tile_id) needed by GM for cleanup.
        """

        intermediate_id = Tile.DOOR_SMALL_OPENING.value

        if self.set_tile_at(pos_x, pos_y, intermediate_id):
            print(f"Door at ({pos_x}, {pos_y}) starting animation.")

            final_id = Tile.DOOR_SMALL_OPENED.value

            # Return the required animation cleanup data: (x, y, final_id)
            return pos_x, pos_y, final_id

        return False  # Door could not be opened

    def process_action(self, pos_x, pos_y, tile_id):
        """
        Handles player interaction or attack at the given tile position.

        Returns:
            bool: False if no action was taken (no lock required).
            tuple: (pos_x, pos_y, final_tile_id) if an action was taken that requires
                   a locked animation delay before the final state is set.
        """
        # --- Handle doors ---
        if tile_id == Tile.DOOR_SMALL_CLOSED.value:
            # We now call the internal method
            return self._open_door_small(pos_x, pos_y)

        # NOTE: Add other interactions here (e.g., chest opening, enemy attack)

        return False  # Action failed or was not found


levels = {
    'test': {
        'terrain': 'data/testLevel.csv',
        # add other layers here later (e.g., 'enemies', 'props')
    }
}
