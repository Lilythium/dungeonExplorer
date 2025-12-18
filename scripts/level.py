import pygame

from scripts.animation import TileSequenceAnimation, InterpolationAnimation
from scripts.entityClasses.ghost import Ghost
from scripts.game_manager import GM
from scripts.level_actions import LevelActions
from scripts.support import import_csv_layout
from scripts.tileset import Tile

levels = {
    'test': {
        'terrain': 'data/testLevel_TileLayer.csv',
        'enemy': 'data/testLevel_EnemyLayer.csv'
    }
}


class Level:
    def __init__(self, level_data, tile_map_loader):
        self.target_offset_y = None
        self.target_offset_x = None
        self.tile_map_loader = tile_map_loader
        self.terrain_data = import_csv_layout(level_data['terrain'])
        self.enemy_data = import_csv_layout(level_data['enemy'])
        self.enemies = pygame.sprite.Group()
        self._enemies_taken_turn_this_phase = set()

        # Track animated tiles - MUST be initialized before setup_level_surface()
        self.animated_tiles: dict[tuple[int, int], TileSequenceAnimation] = {}

        self.level_surface = self.setup_level_surface()
        self.spawn_enemies_from_csv()
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Initialize action handler
        self.actions = LevelActions(self)

    def setup_level_surface(self):
        """Creates a single, large Pygame Surface containing all terrain tiles."""
        if not self.terrain_data:
            return pygame.Surface((0, 0))

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

    def spawn_enemies_from_csv(self):
        """Creates and places enemies based on level data"""
        if not self.enemy_data:
            return

        # Ensure the enemy group is empty before spawning
        self.enemies.empty()

        for row_index, row in enumerate(self.enemy_data):
            for col_index, tile_id_str in enumerate(row):
                tile_index = int(tile_id_str)

                if tile_index != Tile.EMPTY.value:

                    # Determine which enemy type to spawn based on tile_index
                    # NOTE: You must map tile IDs from your enemy layer CSV to specific Enemy classes.

                    if tile_index == Tile.GHOST_LARGE.value:
                        # Instantiate the concrete enemy class
                        new_enemy = Ghost(
                            tile_map_loader=self.tile_map_loader,
                            spawn_x=col_index,
                            spawn_y=row_index
                        )
                        # Add the enemy to the level's enemy group
                        self.enemies.add(new_enemy)

    def get_tile_at(self, pos_x, pos_y):
        """Returns tile ID at x, y."""
        max_rows = len(self.terrain_data)
        max_cols = len(self.terrain_data[0]) if max_rows > 0 else 0

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
            self.terrain_data[pos_y][pos_x] = str(new_tile_id)
            self.level_surface = self.setup_level_surface()
            return True
        return False

    def is_walkable(self, target_x, target_y):
        """Helper function to check if tile is walkable"""
        return self.get_tile_at(target_x, target_y) in Tile.get_walkable_tiles()

    def get_enemy_at(self, pos_x, pos_y):
        """
        Returns the enemy at the given grid position, or None if no enemy there
        Args:
            pos_x: Grid X position
            pos_y: Grid Y position

        Returns:
            Enemy object if found, None otherwise
        """
        for enemy in self.enemies:
            if enemy.is_alive and enemy.grid_x == pos_x and enemy.grid_y == pos_y:
                return enemy
        return None

    def set_initial_camera_position(self, offset_x, offset_y):
        """
        Sets the initial camera position without animation.
        Should be called once after player is positioned.
        """
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)
        self.target_offset_x = float(offset_x)
        self.target_offset_y = float(offset_y)

    def animate_camera_to(self, target_offset_x, target_offset_y, duration_frames=None):
        """
        Smoothly animates the camera from current position to target position.

        Args:
            target_offset_x: Target X offset
            target_offset_y: Target Y offset
            duration_frames: Animation duration (defaults to GM.ANIMATION_DELAY_FRAMES)
        """

        if duration_frames is None:
            duration_frames = GM.ANIMATION_DELAY_FRAMES

        # Store the starting position
        start_offset_x = self.offset_x
        start_offset_y = self.offset_y

        # Store target
        self.target_offset_x = target_offset_x
        self.target_offset_y = target_offset_y

        # Create interpolation animation for offset_x
        offset_x_animation = InterpolationAnimation(
            target_object=self,
            property_name='offset_x',
            start_value=start_offset_x,
            end_value=target_offset_x,
            duration_frames=duration_frames,
            easing_function=InterpolationAnimation.ease_in_out_quad
        )

        # Create interpolation animation for offset_y
        offset_y_animation = InterpolationAnimation(
            target_object=self,
            property_name='offset_y',
            start_value=start_offset_y,
            end_value=target_offset_y,
            duration_frames=duration_frames,
            easing_function=InterpolationAnimation.ease_in_out_quad
        )

        # Add both animations
        GM.add_animation(offset_x_animation)
        GM.add_animation(offset_y_animation)

    def draw(self, display_surface):
        """
        Draws the single, pre-rendered map surface to the display.
        Uses the animated offset values for smooth camera movement.
        """
        # Rebuild surface if there are animated tiles
        if self.animated_tiles:
            self.level_surface = self.setup_level_surface()

        display_surface.blit(self.level_surface, (round(self.offset_x), round(self.offset_y)))

        self.enemies.update()
        self.enemies.draw(display_surface)

    def process_action(self, pos_x, pos_y, tile_id):
        """
        Handles player interaction or attack at the given tile position.
        Delegates to the appropriate action handler.
        """

        # Route to appropriate action handler
        if tile_id == Tile.DOOR_SMALL_CLOSED.value:
            return self.actions.open_door_small(pos_x, pos_y)

        elif tile_id == Tile.DOOR_LEFT_CLOSED.value:
            return self.actions.open_door_left(pos_x, pos_y)

        elif tile_id == Tile.DOOR_RIGHT_CLOSED.value:
            return self.actions.open_door_right(pos_x, pos_y)

        elif tile_id == Tile.CHEST_CLOSED.value:
            return self.actions.open_chest(pos_x, pos_y)

        elif tile_id in {
            Tile.FOUNTAIN_BOTTOM_OFF.value,
            Tile.FOUNTAIN_BOTTOM_ON.value,
            Tile.FOUNTAIN_BOTTOM_OFF_GRATE.value,
            Tile.FOUNTAIN_BOTTOM_ON_GRATE.value
        }:
            return self.actions.activate_fountain(pos_x, pos_y, tile_id)

        # Add more action types here as needed

        return False  # No valid action found

    def execute_enemy_turns(self):
        """
        The main AI driver for the level. Called by the GameManager once the
        player's turn is finished and animations are resolved.
        Returns True if any enemy took an action, False otherwise.
        """
        if not self.enemies:
            print("[ENEMY DEBUG] No enemies to process")
            return False

        player_pos = GM.player.get_grid_pos()
        print(f"[ENEMY DEBUG] Processing {len(self.enemies)} enemies")

        any_actions_taken = False

        # Iterate over a copy of the group to allow removal (death) during iteration
        for enemy in list(self.enemies):
            # Check if enemy is ready, alive, and hasn't taken a turn this phase
            enemy_id = id(enemy)  # Unique identifier for each enemy

            if (enemy.is_alive and not enemy.is_moving and
                    enemy_id not in self._enemies_taken_turn_this_phase):

                print(f"[ENEMY DEBUG] Enemy at {enemy.get_grid_pos()} taking turn")
                self._enemies_taken_turn_this_phase.add(enemy_id)

                # take_turn() will handle both decision-making AND execution
                # It returns True if an action was taken
                action_taken = enemy.take_turn(player_pos)

                if action_taken:
                    any_actions_taken = True
                    print(f"[ENEMY DEBUG] Enemy took action")
                else:
                    print(f"[ENEMY DEBUG] Enemy could not act")
            else:
                if not enemy.is_alive:
                    print(f"[ENEMY DEBUG] Enemy is dead, skipping")
                elif enemy.is_moving:
                    print(f"[ENEMY DEBUG] Enemy is still moving, skipping")
                elif enemy_id in self._enemies_taken_turn_this_phase:
                    print(f"[ENEMY DEBUG] Enemy already took turn this phase, skipping")

        return any_actions_taken

    def reset_enemy_turn_tracking(self):
        """Reset which enemies have taken their turn for the current phase."""
        self._enemies_taken_turn_this_phase.clear()
