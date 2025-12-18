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

            # --- Initialize core game attributes ---
            cls._instance.current_level = None
            cls._instance.player = None
            cls._instance.death_cloud = None
            cls._instance.render_tile_size = 0
            cls._instance.screen_width = 0
            cls._instance.screen_height = 0

            # --- Initialize animation manager ---
            cls._instance.animation_manager = AnimationManager()
            cls._instance.ANIMATION_DELAY_FRAMES = 30

            # --- State machine (will be initialized in main.py) ---
            cls._instance.state_machine = None

        return cls._instance

    @property
    def is_locked(self):
        """Returns whether the game is locked due to active animations."""
        return self.has_animations()

    def has_animations(self):
        """Check if any animations are currently running."""
        return self.animation_manager.is_animating()

    def add_animation(self, animation: Animation):
        """Add an animation to the manager."""
        self.animation_manager.add_animation(animation)

    def resolve_animations(self):
        """
        Called every frame to update all active animations.
        Returns True if animations are still running.
        """
        return self.animation_manager.update()

    def start_enemy_turn(self):
        """Start enemy turn processing."""
        print("[STATE] Starting enemy turn")

        # --- Execute enemy actions ---
        if self.current_level:
            enemy_actions_taken = self.current_level.execute_enemy_turns()

            # --- Check if there are any animations running ---
            if self.has_animations() or enemy_actions_taken:
                # Wait for animations to complete in the main loop
                # The main loop will handle the transition
                pass
            else:
                # --- No actions and no animations, go directly back to player turn ---
                print("[STATE] No enemy actions and no animations, moving directly back to player turn")
                if self.state_machine:
                    self.state_machine.enemy_turn_complete()
                    # --- Start new player movement phase ---
                    self.player.start_movement_phase()


# --- Create a globally accessible instance of the Manager ---
GM = GameManager()
