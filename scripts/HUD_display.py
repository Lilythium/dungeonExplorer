import pygame

from scripts.animation import EntityFrameAnimation, AnimationManager
from scripts.game_manager import GM
from scripts.support import SpriteSheet


class HUD_Manager:
    """
    Manages and draws all Heads-Up Display elements.
    Provides a single interface for game logic to draw and update the HUD.
    """

    def __init__(self, spritesheet_loader):
        self.spritesheet_loader = spritesheet_loader

        # Separate animation manager for HUD (doesn't lock game state)
        self.hud_animation_manager = AnimationManager()

        # --- Create and manage the HealthBar ---
        self.health_bar = HealthBar(
            spritesheet_loader=self.spritesheet_loader,
            hud_animation_manager=self.hud_animation_manager,  # Pass the HUD-specific manager
            start_x=10,
            start_y=10
        )

    def reset(self):
        """
        Reset HUD state when starting a new game.
        Useful for clearing animations and resetting to initial state.
        """
        # Clear any ongoing HUD animations
        self.hud_animation_manager.clear_all()
        # Recreate health bar with current player health
        self.health_bar = HealthBar(
            spritesheet_loader=self.spritesheet_loader,
            hud_animation_manager=self.hud_animation_manager,
            start_x=10,
            start_y=10
        )

    def update_health(self, new_health: int):
        """
        Public method for game logic (e.g., player hit) to trigger a health refresh.
        """
        self.health_bar.set_health(new_health)

    def draw(self, display_surface):
        """Draws all HUD elements"""
        # Draw the Health Bar
        self.health_bar.draw(display_surface)

    def update(self):
        """Updates all animated HUD elements (delegated)."""
        # Update HUD animations (doesn't affect game state)
        self.hud_animation_manager.update()
        # Update the Health Bar
        self.health_bar.update()


class Heart(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, int], spritesheet_loader, hud_animation_manager):
        super().__init__()
        self.rect = pygame.Rect(position, (GM.render_tile_size, GM.render_tile_size))

        self.state: str = 'blank'  # 'full', 'empty', 'blank'
        self.is_animating: bool = False
        target_size = (GM.render_tile_size, GM.render_tile_size)

        # --- Load Static Images ---
        self.image_full = pygame.image.load("graphics/hearts/heart_normal_full.png").convert_alpha()
        self.image_full = pygame.transform.scale(self.image_full, target_size)
        self.image_empty = pygame.image.load("graphics/hearts/heart_empty.png").convert_alpha()
        self.image_empty = pygame.transform.scale(self.image_empty, target_size)

        # --- Animation Sheets (Must be FrameSequenceAnimation compatible) ---
        self.heart_spawn_sheet = SpriteSheet("graphics/hearts/heart_normal_spawn_full.png", 16, 16, 2)
        self.heart_blink_sheet = SpriteSheet("graphics/hearts/heart_normal_blink_full.png", 16, 16, 2)

        self.image = pygame.Surface((GM.render_tile_size, GM.render_tile_size),
                                    pygame.SRCALPHA)  # Start as blank/transparent
        self.kill_switch_active: bool = False  # Used to kill the sprite on final empty state

        # Reference to HUD animation manager (not GameManager)
        self.hud_animation_manager = hud_animation_manager

    def spawn(self, on_sequence_complete=None):
        """Plays the spawn animation and sets the heart to 'full'."""
        if self.is_animating:
            return
        self.is_animating = True
        self.state = 'full'
        self.kill_switch_active = False

        def on_spawn_complete():
            self.is_animating = False
            # Replace the animation image with the static full image
            self.image = self.image_full
            if on_sequence_complete:
                on_sequence_complete()

        # Create an entity frame animation
        spawn_animation = EntityFrameAnimation(
            target_object=self,
            property_name='image',
            spritesheet=self.heart_spawn_sheet,
            frame_duration=3,  # Frames per sprite frame
            on_complete_callback=on_spawn_complete
        )

        # Use HUD animation manager, not GameManager
        self.hud_animation_manager.add_animation(spawn_animation)

    def empty(self, remove_from_group: bool = False, blinks_remaining: int = 1):
        """Plays the blink animation and sets the heart to 'empty'."""
        if self.is_animating:
            return
        self.is_animating = True
        self.kill_switch_active = remove_from_group

        def on_blink_complete():
            self.is_animating = False

            if blinks_remaining > 0:
                self.empty(remove_from_group, blinks_remaining - 1)
            else:
                # Replace the animation image with the static empty image
                self.image = self.image_empty
                self.state = 'empty'

                if self.kill_switch_active:
                    self.kill()  # Remove from sprite group if max health decreases

        # Create a frame sequence animation (blinking)
        blink_animation = EntityFrameAnimation(
            target_object=self,
            property_name='image',
            spritesheet=self.heart_blink_sheet,
            frame_duration=4,
            on_complete_callback=on_blink_complete
        )

        # Use HUD animation manager, not GameManager
        self.hud_animation_manager.add_animation(blink_animation)

    def update(self):
        pass


class HealthBar:
    """
    Manages a group of Heart sprites
    """

    def __init__(self, spritesheet_loader, hud_animation_manager, start_x=10, start_y=10):
        self.player = GM.player
        self.spritesheet_loader = spritesheet_loader

        # Store HUD animation manager reference
        self.hud_animation_manager = hud_animation_manager

        self.max_health = self.player.max_health
        self.num_hearts = self.max_health

        self.heart_group = pygame.sprite.Group()
        self.hearts: list[Heart] = []

        # Layout properties
        self.heart_spacing = GM.render_tile_size + 4
        self.start_x = start_x
        self.start_y = start_y

        self._create_hearts()
        self._initial_spawn_sequence(0)

    def _create_hearts(self):
        """Initializes all Heart sprites in a row."""
        for i in range(self.num_hearts):
            x = self.start_x + (i * self.heart_spacing)
            y = self.start_y

            # Instantiate the Heart using the class reference passed in
            new_heart = Heart(
                position=(x, y),
                spritesheet_loader=self.spritesheet_loader,
                hud_animation_manager=self.hud_animation_manager  # Pass HUD animation manager
            )
            self.hearts.append(new_heart)
            self.heart_group.add(new_heart)

            # Start all hearts blank
            new_heart.image = pygame.Surface((GM.render_tile_size, GM.render_tile_size), pygame.SRCALPHA)
            new_heart.state = 'blank'

    def start_initial_animation(self):
        """Start the initial spawn animation for the hearts."""
        self._initial_spawn_sequence(0)

    def _initial_spawn_sequence(self, index: int):
        """
        Sequentially spawns hearts up to the player's initial hit_points
        Called once during initialization.
        """
        if index >= self.player.current_health or index >= self.num_hearts:
            return

        heart = self.hearts[index]

        # The custom callback that triggers the NEXT heart's animation
        def chain_spawn_callback():
            # Trigger the next heart's animation after this one completes
            self._initial_spawn_sequence(index + 1)

        # Start the spawn animation for the current heart
        heart.spawn(on_sequence_complete=chain_spawn_callback)

    def set_health(self, new_health: int):
        """
        Refreshes the heart states based on the current health value.
        Triggers spawn/empty animations on individual hearts.
        """
        for i, heart in enumerate(self.hearts):
            if new_health > i:
                if heart.state != 'full':
                    heart.spawn()
            else:
                if heart.state != 'empty':
                    heart.empty(False, 2)

    def draw(self, display_surface):
        """Draws all heart sprites to the screen."""
        self.heart_group.draw(display_surface)

    def update(self):
        """Updates heart sprite animations."""
        self.heart_group.update()
