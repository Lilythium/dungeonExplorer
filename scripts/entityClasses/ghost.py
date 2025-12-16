from scripts.entityClasses.enemy import Enemy
from scripts.game_manager import GM


class Ghost(Enemy):
    def __init__(self, tile_map_loader, spawn_x, spawn_y):
        super().__init__(tile_map_loader, spawn_x, spawn_y)

        self.image = self.tile_map_loader.get_tile(121)
        self.rect = self.image.get_rect()
        self.rect.topleft = (spawn_x * GM.render_tile_size, spawn_y * GM.render_tile_size)

        # test route
        self.patrol_route = [(spawn_x, spawn_y), (spawn_x, spawn_y - 1), (spawn_x, spawn_y - 3)]
