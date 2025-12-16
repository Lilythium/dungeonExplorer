import pygame


class Entity(pygame.sprite.Sprite):

    def __init__(self, tile_map_loader):
        super().__init__()
        self.tile_map_loader = tile_map_loader
        # --- Game Grid State  ---
        self.grid_x = 0
        self.grid_y = 0
        self.facing_dir = (0, 0)

        # These properties will be animated by EntityActions.move_entity
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)

    def get_grid_pos(self):
        """Returns the player's position in the map grid."""
        return self.grid_x, self.grid_y

    def set_grid_pos(self, x, y):
        """Sets the player's starting position in the map grid."""
        self.grid_x = x
        self.grid_y = y

    def sync_visual_offset(self):
        """
        Ensures the visual offset is set to the current logical grid position.
        Called on startup or after a non-animated teleport.
        """
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)

    def perform_queued_action(self):
        """
        Executes the queued action based on self.facing_dir.

        Returns:
            False: Action blocked (no turn consumed).
            True: Simple move action (triggers animation lock, no tile swap needed).
            tuple: (pos_x, pos_y, final_tile_id) if an interaction/attack needs cleanup.
        """
        pass

    def update(self):
        """
        Player stays centered - camera movement handles positioning.
        """
        pass
