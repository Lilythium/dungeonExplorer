import pygame

from scripts.entityClasses.entity import Entity
from scripts.entity_actions import move_player_path, move_player
from scripts.game_manager import GM
from scripts.pathfinding import get_reachable_tiles, find_path_bfs
from scripts.tileset import Tile


class Player(Entity):
    COLOUR_GREEN = (0, 200, 0, 255)
    COLOUR_RED = (200, 0, 0, 255)
    COLOUR_BLUE = (100, 150, 255, 160)
    COLOUR_BLUE_DARK = (60, 90, 180, 200)

    def __init__(self, tile_map_loader):
        super().__init__(tile_map_loader)
        self.tile_map_loader = tile_map_loader

        # --- Movement Stats ---
        self.move_speed = 3

        # --- Sprite Setup ---
        self.image = self.tile_map_loader.get_tile(Tile.PLAYER_CHARACTER.value)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()

        self.selector = self.tile_map_loader.get_tile(Tile.SELECTOR.value)
        self.selector_rect = self.selector.get_rect()

        self.facing_dir = (0, 0)

        # --- Movement Phase State ---
        self.cursor_x = 0
        self.cursor_y = 0
        self.reachable_tiles = set()
        self.movement_confirmed = False

        # --- Positioning ---
        self.rect.centerx = GM.screen_width // 2
        self.rect.centery = GM.screen_height // 2

        # --- Visual Animation State ---
        self.offset_x_visual = float(self.grid_x)
        self.offset_y_visual = float(self.grid_y)
        self.squash_x = 1.0
        self.squash_y = 1.0

        self.slide_x = 0.0
        self.slide_y = 0.0
        self.start_grid_x = self.grid_x
        self.start_grid_y = self.grid_y
        self.is_moving = False

        # --- Combat Stats ---
        self.attack_dmg = 1
        self.max_health = 3
        self.current_health = self.max_health

        # --- Create movement highlight surfaces ---
        self.highlight_surf = pygame.Surface((GM.render_tile_size, GM.render_tile_size), pygame.SRCALPHA)
        self.highlight_surf.fill(self.COLOUR_BLUE)

        self.highlight_outline = pygame.Surface((GM.render_tile_size, GM.render_tile_size), pygame.SRCALPHA)
        pygame.draw.rect(self.highlight_outline, self.COLOUR_BLUE_DARK,
                         (0, 0, GM.render_tile_size, GM.render_tile_size), 2)

        # --- Movement range animation ---
        self.range_reveal_progress = 0.0
        self.range_reveal_speed = 0.15

    def set_grid_pos(self, x, y):
        """Sets the player's starting position in the map grid."""
        self.grid_x = x
        self.grid_y = y
        self.offset_x_visual = float(x)
        self.offset_y_visual = float(y)
        self.cursor_x = x
        self.cursor_y = y

    def start_movement_phase(self):
        """Initialize movement phase - calculate reachable tiles."""
        self.cursor_x = self.grid_x
        self.cursor_y = self.grid_y
        self.reachable_tiles = get_reachable_tiles(
            GM.current_level,
            self.grid_x,
            self.grid_y,
            self.move_speed,
            ignore_enemies=True
        )
        self.movement_confirmed = False
        self.range_reveal_progress = 0.0
        print(f"[PLAYER] Movement phase started. Reachable tiles: {len(self.reachable_tiles)}")

    def move_cursor(self, dx, dy):
        """Move the movement cursor, constrained to reachable tiles."""
        new_x = self.cursor_x + dx
        new_y = self.cursor_y + dy

        if (new_x, new_y) in self.reachable_tiles:
            self.cursor_x = new_x
            self.cursor_y = new_y
            return True
        return False

    def confirm_movement(self):
        """Confirm movement to cursor position."""
        if (self.cursor_x, self.cursor_y) not in self.reachable_tiles:
            return False

        # --- Don't move if already at cursor position ---
        if self.cursor_x == self.grid_x and self.cursor_y == self.grid_y:
            self.movement_confirmed = True
            GM.state_machine.player_movement_complete()
            self.start_action_phase()
            return True

        # --- Check if destination has an enemy ---
        if GM.current_level.get_enemy_at(self.cursor_x, self.cursor_y):
            print("[PLAYER] Cannot move to tile with enemy")
            return False

        # --- Find path to destination ---
        path = find_path_bfs(GM.current_level, self.grid_x, self.grid_y,
                             self.cursor_x, self.cursor_y, self.move_speed)

        if not path or len(path) < 2:
            return False

        print(f"[PLAYER] Moving along path: {path}")

        # --- Callback for when entire path is complete ---
        def on_path_complete():
            self.sync_visual_offset()
            self.is_moving = False
            if self.can_perform_action():
                self.start_action_phase()
                GM.state_machine.player_movement_complete()
            else:
                GM.state_machine.player_has_no_action()

        # --- Start multi-tile movement ---
        move_player_path(self, path, on_complete_callback=on_path_complete)
        self.is_moving = True
        self.movement_confirmed = True

        return True

    def start_action_phase(self):
        """Initialize action phase."""
        self.facing_dir = (0, 0)
        print("[PLAYER] Action phase started")

    def get_action_target(self):
        """Get the position being targeted for action."""
        if self.facing_dir == (0, 0):
            return None

        dx, dy = self.facing_dir
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        return target_x, target_y

    def set_facing_direction(self, dx, dy):
        """Set the direction player is facing for action phase."""
        self.facing_dir = (dx, dy)

    def can_perform_action(self):
        """Check for interact or attack targets in range"""
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                if dx != 0 and dy != 0:
                    continue
                target_x = self.grid_x + dx
                target_y = self.grid_y + dy

                tile_id = GM.current_level.get_tile_at(target_x, target_y)
                if tile_id in Tile.get_selectable_tiles():
                    return True

                if GM.current_level.get_enemy_at(target_x, target_y):
                    return True
        return False

    def perform_action(self):
        """Execute action in the direction player is facing."""
        if self.facing_dir == (0, 0):
            GM.state_machine.player_skip_action()
            return True

        dx, dy = self.facing_dir
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        target_tile_index = GM.current_level.get_tile_at(target_x, target_y)

        # --- Check for ATTACK ---
        attack_target = GM.current_level.get_enemy_at(target_x, target_y)
        if attack_target:
            self.attack_enemy(attack_target)
            self.facing_dir = (0, 0)
            return True

        # --- Check for INTERACTION ---
        if target_tile_index in Tile.get_selectable_tiles():
            animation_info = GM.current_level.process_action(target_x, target_y, target_tile_index)
            if animation_info:
                print(f"[PLAYER] Initiated action on tile ID {target_tile_index}")
                self.facing_dir = (0, 0)
                return True

        print("[PLAYER] No valid action in that direction")
        return False

    def draw_movement_range(self, surface):
        """Draw highlighted tiles showing movement range with grow-out effect."""
        if not self.reachable_tiles:
            return

        # --- Update reveal animation ---
        if self.range_reveal_progress < 1.0:
            self.range_reveal_progress = min(1.0, self.range_reveal_progress + self.range_reveal_speed)

        # --- Calculate distances for reveal effect ---
        tile_distances = {}
        for tile_x, tile_y in self.reachable_tiles:
            if tile_x == self.grid_x and tile_y == self.grid_y:
                continue
            distance = abs(tile_x - self.grid_x) + abs(tile_y - self.grid_y)
            tile_distances[(tile_x, tile_y)] = distance

        max_distance = max(tile_distances.values()) if tile_distances else 1
        revealed_distance = max_distance * self.range_reveal_progress

        # --- Draw tiles ---
        for tile_x, tile_y in self.reachable_tiles:
            if tile_x == self.grid_x and tile_y == self.grid_y:
                continue

            distance = tile_distances.get((tile_x, tile_y), 0)
            if distance > revealed_distance:
                continue

            screen_x = (tile_x * GM.render_tile_size) + GM.current_level.offset_x
            screen_y = (tile_y * GM.render_tile_size) + GM.current_level.offset_y

            # --- Draw fill ---
            surface.blit(self.highlight_surf, (screen_x, screen_y))
            # --- Draw outline ---
            surface.blit(self.highlight_outline, (screen_x, screen_y))

    def draw_movement_cursor(self, surface):
        """Draw the cursor showing where player will move."""
        if self.cursor_x != self.grid_x or self.cursor_y != self.grid_y:
            screen_x = (self.cursor_x * GM.render_tile_size) + GM.current_level.offset_x
            screen_y = (self.cursor_y * GM.render_tile_size) + GM.current_level.offset_y

            cursor_colored = self.selector.copy()
            cursor_colored.fill((255, 255, 255, 255), special_flags=pygame.BLEND_MULT)
            surface.blit(cursor_colored, (screen_x, screen_y))

    def get_colored_selector(self, colour):
        """Creates a temporary, colored version of the selector sprite."""
        colored_selector = self.selector.copy()
        colored_selector.fill(colour, special_flags=pygame.BLEND_MULT)
        return colored_selector

    def draw_action_selector(self, surface):
        """Draw the selector for action phase."""
        if self.facing_dir == (0, 0):
            return

        dx, dy = self.facing_dir
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        screen_x = (target_x * GM.render_tile_size) + GM.current_level.offset_x
        screen_y = (target_y * GM.render_tile_size) + GM.current_level.offset_y

        target_tile_index = GM.current_level.get_tile_at(target_x, target_y)

        if GM.current_level.get_enemy_at(target_x, target_y):
            surface.blit(self.get_colored_selector(self.COLOUR_RED), (screen_x, screen_y))
        elif target_tile_index in Tile.get_selectable_tiles():
            surface.blit(self.get_colored_selector(self.COLOUR_GREEN), (screen_x, screen_y))
        else:
            surface.blit(self.selector, (screen_x, screen_y))

    def attack_enemy(self, enemy):
        enemy.take_damage(self.attack_dmg, self.facing_dir)

    def take_damage(self, amount: int, direction: tuple[int, int], suppress_state_transition: bool = False):
        """
        Player takes damage and gets knocked back.

        Args:
            amount: Damage to take
            direction: Direction of knockback
            suppress_state_transition: If True, don't trigger state transition (used during enemy turn)
        """
        self.current_health -= amount
        new_x, new_y = self.get_grid_pos()
        new_x += -direction[0]
        new_y += -direction[1]

        # --- Move player without triggering state transition ---
        if suppress_state_transition:
            # Manually create the animation without calling move_player
            from scripts.animation import InterpolationAnimation

            start_visual_x = self.offset_x_visual
            start_visual_y = self.offset_y_visual

            # --- DON'T update grid position yet ---
            self.is_moving = True

            duration_frames = 8

            # Calculate camera target
            player_pixel_x = new_x * GM.render_tile_size
            player_pixel_y = new_y * GM.render_tile_size
            target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
            target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

            def on_movement_complete():
                # --- Update grid position NOW ---
                self.grid_x = new_x
                self.grid_y = new_y
                self.sync_visual_offset()
                self.is_moving = False

            # --- Animate visual offset ---
            player_visual_x_anim = InterpolationAnimation(
                target_object=self,
                property_name='offset_x_visual',
                start_value=start_visual_x,
                end_value=float(new_x),
                duration_frames=duration_frames,
                easing_function=InterpolationAnimation.ease_out_quad,
                on_complete_callback=on_movement_complete
            )

            player_visual_y_anim = InterpolationAnimation(
                target_object=self,
                property_name='offset_y_visual',
                start_value=start_visual_y,
                end_value=float(new_y),
                duration_frames=duration_frames,
                easing_function=InterpolationAnimation.ease_out_quad
            )

            # --- Animate camera ---
            GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=duration_frames)

            # Add animations
            GM.add_animation(player_visual_x_anim)
            GM.add_animation(player_visual_y_anim)
        else:
            # Normal player turn damage - use move_player
            def on_damage_complete():
                self.sync_visual_offset()
                self.is_moving = False

            move_player(self, new_x, new_y, duration_frames=8, on_complete_callback=on_damage_complete)

        self.start_damage_flash()
        GM.hud_manager.update_health(self.current_health)

        if self.current_health <= 0:
            self.game_over()

    def update(self):
        """Update player's visual position based on animated offset."""
        center_x = GM.screen_width // 2
        center_y = GM.screen_height // 2

        self.update_damage_flash()

        # Update image for squash/stretch effect
        if not self.is_flashing:
            if self.is_moving and (self.squash_x != 1.0 or self.squash_y != 1.0):
                new_width = int(self.original_image.get_width() * self.squash_x)
                new_height = int(self.original_image.get_height() * self.squash_y)
                self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            elif not self.is_moving:
                self.image = self.original_image.copy()

        # Calculate pixel offset from visual animation
        # The player stays visually centered, while offset_x_visual tracks logical position
        pixel_offset_x = (self.offset_x_visual - float(self.grid_x)) * GM.render_tile_size
        pixel_offset_y = (self.offset_y_visual - float(self.grid_y)) * GM.render_tile_size

        # Player stays centered on screen
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x + pixel_offset_x
        self.rect.centery = center_y + pixel_offset_y

        if self.is_moving:
            if self.is_moving:
                print(
                    f"grid=({self.grid_x},{self.grid_y}), offset=({self.offset_x_visual:.3f},{self.offset_y_visual:.3f}),"
                    f" pixel=({pixel_offset_x:.1f},{pixel_offset_y:.1f})")

    @staticmethod
    def game_over():
        if GM.state_machine:
            GM.state_machine.game_over_transition()
