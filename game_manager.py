# game_manager.py

class GameManager:
    """
    Holds the single, authoritative instances of key game objects
    (Level, Player) for easy global access throughout the game.
    """

    # Static variable to hold the single instance of the manager
    _instance = None

    # NOTE: The __init__ method has been removed, as the __new__ method handles
    # all single-time initialization for the Singleton pattern.

    def __new__(cls):
        """Ensures only one instance of GameManager can be created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)

            # Initialize core game attributes on the first call
            cls._instance.current_level = None
            cls._instance.player = None
            cls._instance.render_tile_size = 0
            cls._instance.screen_width = 0
            cls._instance.screen_height = 0

            # --- Animation and Lock State ---
            cls._instance.is_locked = False
            cls._instance.ANIMATION_DELAY_FRAMES = 30  # Constant for default duration
            cls._instance.animation_timer = 0

            # A list to hold multiple simultaneous animations (e.g., door opening AND an enemy moving)
            cls._instance.active_animations = []

        return cls._instance

    def lock_game_and_start_animations(self, duration_frames=None):
        """
        Locks player input and starts the animation timer.
        """
        self.is_locked = True
        self.animation_timer = duration_frames or self.ANIMATION_DELAY_FRAMES

    def resolve_animations(self):
        """
        Called every frame to decrement the timer and check if the lock should be released.
        Returns: True if the game is still locked.
        """
        if not self.is_locked:
            return False

        self.animation_timer -= 1

        # NOTE: Animation processing for specific sprites/tiles would be handled here
        # using the data stored in self.active_animations (to be implemented next).

        if self.animation_timer <= 0:
            self.is_locked = False

            # Once the lock is released, trigger the rest of the turn's events
            # This is the crucial transition point in the turn cycle.
            self.handle_turn()

            return False  # Lock released

        return True  # Game is still locked and animating

    def handle_turn(self):
        """
        Called after the player's action and ALL animations are resolved.
        This is the global trigger for the rest of the game world's actions.
        """
        print("--- Turn Resolution (Post-Animation) ---")
        # Enemy movement, trap checks, status effect decay, etc., happen here.

        print("--- Turn End ---")


# Create a globally accessible instance of the Manager
GM = GameManager()
