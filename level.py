from animation import FrameSequenceAnimation
from game_manager import GM
from support import import_csv_layout

levels = {
    'test': {
        'terrain': 'data/testLevel.csv',
        # add other layers here later (e.g., 'enemies', 'props')
    }
}


class Level:
    def __init__(self, level_data, tile_map_loader):
        self.tile_map_loader = tile_map_loader
        self.terrain_data = import_csv_layout(level_data['terrain'])

        # Track animated tiles
        self.animated_tiles: dict[tuple[int, int], FrameSequenceAnimation] = {}
        self.level_surface = self.setup_level_surface()
        self.offset_x = 0
        self.offset_y = 0

    def setup_level_surface(self):
        """Creates a single, large Pygame Surface containing all terrain tiles."""
        import pygame
        if not self.terrain_data:
            return pygame.Surface((0, 0))

        from tileset import Tile
        sample_sprite = self.tile_map_loader.get_tile(Tile.GROUND.value)
        tile_width = sample_sprite.get_width()
        tile_height = sample_sprite.get_height()

        map_width = len(self.terrain_data[0]) * tile_width
        map_height = len(self.terrain_data) * tile_height

        map_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for row_index, row in enumerate(self.terrain_data):
            for col_index, tile_id_str in enumerate(row):
                tile_index = int(tile_id_str)

                if tile_index != Tile.EMPTY.value:
                    # Check if this position has an active animation
                    pos_key = (col_index, row_index)
                    if pos_key in self.animated_tiles:
                        anim = self.animated_tiles[pos_key]
                        tile_index = anim.get_current_tile_id()

                    sprite = self.tile_map_loader.get_tile(tile_index)
                    x = col_index * tile_width
                    y = row_index * tile_height
                    map_surface.blit(sprite, (x, y))

        return map_surface

    def get_tile_at(self, pos_x, pos_y):
        """Returns tile ID at x, y."""
        max_rows = len(self.terrain_data)
        max_cols = len(self.terrain_data[0]) if max_rows > 0 else 0

        if not (0 <= pos_x < max_cols):
            from tileset import Tile
            return Tile.EMPTY.value
        if not (0 <= pos_y < max_rows):
            from tileset import Tile
            return Tile.EMPTY.value

        return int(self.terrain_data[pos_y][pos_x])

    def set_tile_at(self, pos_x, pos_y, new_tile_id):
        """Sets the tile ID at the given grid coordinates."""
        max_rows = len(self.terrain_data)
        max_cols = len(self.terrain_data[0]) if max_rows > 0 else 0

        if 0 <= pos_x < max_cols and 0 <= pos_y < max_rows:
            self.terrain_data[pos_y][pos_x] = str(new_tile_id)
            self.level_surface = self.setup_level_surface()
            return True
        return False

    def draw(self, display_surface, offset_x=0, offset_y=0):
        """
        Draws the single, pre-rendered map surface to the display.
        Updates the surface if there are active tile animations.
        """
        self.offset_x = offset_x
        self.offset_y = offset_y

        # Rebuild surface if there are animated tiles
        if self.animated_tiles:
            self.level_surface = self.setup_level_surface()

        display_surface.blit(self.level_surface, (offset_x, offset_y))

    def _open_door_small(self, pos_x, pos_y):
        """
        Initiates the door opening sequence using frame animation.
        """
        from tileset import Tile

        # Define the animation sequence
        frame_sequence = [
            Tile.DOOR_SMALL_CLOSED.value,
            Tile.DOOR_SMALL_OPENING.value,
            Tile.DOOR_SMALL_OPENED.value
        ]

        def on_complete(x, y, final_id):
            """Callback when animation completes."""
            self.set_tile_at(x, y, final_id)
            # Remove from animated tiles
            pos_key = (x, y)
            if pos_key in self.animated_tiles:
                del self.animated_tiles[pos_key]

        # Create the animation
        animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES,
            on_complete_callback=on_complete
        )

        # Track this tile as animated
        self.animated_tiles[(pos_x, pos_y)] = animation

        # Add to global animation manager
        GM.add_animation(animation)

        print(f"Door at ({pos_x}, {pos_y}) starting animation.")
        return True

    def process_action(self, pos_x, pos_y, tile_id):
        """
        Handles player interaction or attack at the given tile position.
        """
        from tileset import Tile

        if tile_id == Tile.DOOR_SMALL_CLOSED.value:
            return self._open_door_small(pos_x, pos_y)

        # Add other interactions here
        return False
