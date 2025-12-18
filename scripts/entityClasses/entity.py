import pygame


class Entity(pygame.sprite.Sprite):

    def __init__(self, tile_map_loader):
        super().__init__()
        self.tile_map_loader = tile_map_loader
        # --- Game Grid State  ---
        self.grid_x = 0
        self.grid_y = 0
        self.facing_dir = (0, 0)

        # --- Movement Stats ---
        self.move_speed = 1  # Number of tiles entity can move per turn

        # These properties will be animated by EntityActions.move_entity
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)

        # --- Damage Flash Effect ---
        self.image = None
        self.original_image = None
        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 21  # Total frames to flash
        self.flash_interval = 5  # Frames between each flash toggle
        self.flash_color = (255, 255, 255, 255)

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

    def start_damage_flash(self):
        """Initiates the damage flash effect."""
        self.is_flashing = True
        self.flash_timer = 0

    def update_damage_flash(self):
        """
        Updates the damage flash effect.
        Should be called in the entity's update() method.
        Requires self.original_image to be set.
        """
        if not self.is_flashing:
            return

        self.flash_timer += 1

        # --- Determine if we should show the flash or normal sprite ---
        flash_cycle = (self.flash_timer // self.flash_interval) % 2

        if flash_cycle == 1:
            mask = pygame.mask.from_surface(self.original_image)
            flash_image = mask.to_surface(setcolor=self.flash_color, unsetcolor=(0, 0, 0, 0))

            # 3. Apply squash (copy-pasted from your existing logic)
            if hasattr(self, 'squash_x') and hasattr(self, 'squash_y'):
                if self.squash_x != 1.0 or self.squash_y != 1.0:
                    new_width = int(flash_image.get_width() * self.squash_x)
                    new_height = int(flash_image.get_height() * self.squash_y)
                    self.image = pygame.transform.scale(flash_image, (new_width, new_height))
                else:
                    self.image = flash_image
            else:
                self.image = flash_image
        else:
            # --- Show normal sprite ---
            if hasattr(self, 'squash_x') and hasattr(self, 'squash_y'):
                if self.squash_x != 1.0 or self.squash_y != 1.0:
                    new_width = int(self.original_image.get_width() * self.squash_x)
                    new_height = int(self.original_image.get_height() * self.squash_y)
                    self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
                else:
                    self.image = self.original_image.copy()
            else:
                self.image = self.original_image.copy()

        # --- End flash effect after duration ---
        if self.flash_timer >= self.flash_duration:
            self.is_flashing = False
            self.flash_timer = 0
            self.image = self.original_image.copy()

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
