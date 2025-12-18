from scripts.entityClasses.enemy import Enemy
from scripts.game_manager import GM


class Ghost(Enemy):
    def __init__(self, tile_map_loader, spawn_x, spawn_y):
        super().__init__(tile_map_loader, spawn_x, spawn_y)

        # --- Movement Stats ---
        self.move_speed = 1  # Ghost moves 1 tile per turn

        self.image = self.tile_map_loader.get_tile(121)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (spawn_x * GM.render_tile_size, spawn_y * GM.render_tile_size)

        # --- Patrol Waypoints (enemy will pathfind to each in order) ---
        self.patrol_waypoints = [
            (spawn_x, spawn_y),
            (spawn_x, spawn_y - 1),
            (spawn_x, spawn_y - 3)
        ]
        self.current_waypoint_index = 0

        # --- Combat Stats ---
        self.max_health = 100
        self.current_health = self.max_health
