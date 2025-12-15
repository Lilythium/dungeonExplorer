import pygame


class SpriteSheet:
    def __init__(self, filename, tile_width, tile_height, scale_factor=2):
        """Loads the tileset image and stores the tile dimensions."""
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.cols = self.sheet.get_width() // tile_width
        self.rows = self.sheet.get_height() // tile_height
        self.scale_factor = scale_factor

        # Dictionary to store cached individual tile surfaces
        self.tiles = {}

    def get_tile(self, index):
        """
        Extracts a specific tile from the sheet based on its index (0-131).
        If the tile is already extracted, it is returned from the cache.
        """
        if index in self.tiles:
            return self.tiles[index]

        # Calculate the tile's position in the grid
        row = index // self.cols
        col = index % self.cols

        # Calculate the pixel coordinates
        x = col * self.tile_width
        y = row * self.tile_height

        # Create a Surface for the individual tile
        tile_surface = pygame.Surface(
            (self.tile_width, self.tile_height),
            pygame.SRCALPHA
        )

        # Blit (copy) the area of the sprite sheet onto the new surface
        tile_surface.blit(
            self.sheet,
            (0, 0),
            (x, y, self.tile_width, self.tile_height)
        )

        if self.scale_factor != 1:
            new_width = self.tile_width * self.scale_factor
            new_height = self.tile_height * self.scale_factor

            # Use pygame.transform.scale() to resize the surface
            scaled_surface = pygame.transform.scale(
                tile_surface, (new_width, new_height)
            )
            self.tiles[index] = scaled_surface
            return scaled_surface

        # Store in cache and return
        self.tiles[index] = tile_surface
        return tile_surface
