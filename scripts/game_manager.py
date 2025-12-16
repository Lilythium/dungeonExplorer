from scripts.animation import AnimationManager, Animation


class GameManager:
    """
    Holds the single, authoritative instances of key game objects
    (Level, Player) for easy global access throughout the game.
    """
    _instance = None

    def __new__(cls):
        """Ensures only one instance of GameManager can be created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)

            # Initialize core game attributes
            cls._instance.current_level = None
            cls._instance.player = None
            cls._instance.render_tile_size = 0
            cls._instance.screen_width = 0
            cls._instance.screen_height = 0

            # Initialize animation manager
            cls._instance.animation_manager = AnimationManager()
            cls._instance.ANIMATION_DELAY_FRAMES = 30

            # Flag to track if we should process enemy turns after animations
            cls._instance.should_process_enemy_turn = False

        return cls._instance

    @property
    def is_locked(self):
        """Returns whether the game is locked due to active animations."""
        return self.animation_manager.is_locked

    @is_locked.setter
    def is_locked(self, value):
        """Allows external code (like EntityActions) to set the lock state."""
        # Setter writes directly to the AnimationManager's attribute
        self.animation_manager.is_locked = bool(value)

    def add_animation(self, animation: Animation):
        """Add an animation to the manager."""
        self.animation_manager.add_animation(animation)

    def resolve_animations(self):
        """
        Called every frame to update all active animations.
        Returns: True if animations are still running.
        """
        still_animating = self.animation_manager.update()

        # If all animations complete, trigger turn resolution
        if not still_animating and self.should_process_enemy_turn:
            self.handle_turn()

        return still_animating

    def start_turn(self):
        """
        Called by the player when they perform an action.
        This flags that enemy turns should be processed after animations complete.
        """
        print("[TURN DEBUG] Player action initiated - enemy turns will process after animations")
        self.should_process_enemy_turn = True

    def handle_turn(self):
        """
        Called after the player's action and ALL animations are resolved.
        This is the global trigger for the rest of the game world's actions.
        """
        if not self.should_process_enemy_turn:
            print("[TURN DEBUG] No enemy turn needed, skipping")
            return

        print("--- Turn Resolution (Post-Animation) ---")

        # Reset the flag BEFORE processing enemy turns
        # This prevents enemy animations from triggering another handle_turn()
        self.should_process_enemy_turn = False

        # Execute enemy turns
        if self.current_level:
            self.current_level.execute_enemy_turns()

        print("--- Turn End ---")


# Create a globally accessible instance of the Manager
GM = GameManager()
