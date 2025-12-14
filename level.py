from support import import_csv_layout
from tileset import Tile


class Level:
    def __init__(self, level_data, surface, tile_map_loader):
        self.display_surface = surface

        self.tile_map_loader = tile_map_loader

        self.terrain_data = import_csv_layout(level_data['terrain'])

    def draw(self):
        for row_index, row in enumerate(self.terrain_data):
            for col_index, tile_id_str in enumerate(row):

                tile_index = int(tile_id_str)

                # Ignore EMPTY tiles
                if tile_index != Tile.EMPTY.value:
                    # Get sprite Surface
                    sprite = self.tile_map_loader.get_tile(tile_index)

                    # Calculate the pos
                    x = col_index * sprite.get_width()
                    y = row_index * sprite.get_height()

                    self.display_surface.blit(sprite, (x, y))


levels = {
    'test': {
        'terrain': 'data/testLevel.csv',
        # add other layers here later (e.g., 'enemies', 'props')
    }
}
