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
        return self.animation_manager.is_locked

    @is_locked.setter
    def is_locked(self, value):
        """Allows external code (like EntityActions) to set the lock state."""
        self.animation_manager.is_locked = bool(value)

    def add_animation(self, animation: Animation):
        """Add an animation to the manager."""
        self.animation_manager.add_animation(animation)

    def resolve_animations(self):
        """
        Called every frame to update all active animations.
        Handles state transitions when animations complete.
        """
        still_animating = self.animation_manager.update()

        if not self.state_machine:
            return still_animating

        current_state = self.state_machine.current_state.id

        # --- Check if animations are complete and we're in an animating state ---
        if not still_animating:
            if current_state == "player_animating":
                print("[STATE] Player animations complete, moving to enemy turn")
                self.state_machine.player_animations_complete()
                # --- Start enemy turns immediately ---
                self.start_enemy_turn()

            elif current_state == "enemy_animating":
                print("[STATE] Enemy animations complete, moving to player turn")
                self.state_machine.enemy_animations_complete()

        return still_animating

    def start_enemy_turn(self):
        """Start enemy turn processing."""
        print("[STATE] Starting enemy turn")

        # --- Execute enemy actions ---
        if self.current_level:
            enemy_actions_taken = self.current_level.execute_enemy_turns()

            # --- If enemies took actions, transition to enemy_animating ---
            if enemy_actions_taken:
                print("[STATE] Enemy actions taken, moving to enemy animating")
                self.state_machine.enemy_actions_start()
            else:
                # --- Check if there are any animations still running ---
                # (e.g., enemy knockback from player's attack)
                if self.animation_manager.is_animating():
                    print("[STATE] No new enemy actions, but animations still running - moving to enemy animating")
                    self.state_machine.enemy_actions_start()
                else:
                    # --- No actions and no animations, go directly back to player turn ---
                    print("[STATE] No enemy actions and no animations, moving directly back to player turn")
                    self.state_machine.no_enemy_actions()

    def player_perform_action(self):
        """Called when player performs an action to trigger state transition."""
        if self.state_machine and self.state_machine.current_state.id == "player_turn":
            print("[STATE] Player action, moving to player animating state")
            self.state_machine.player_action()


# --- Create a globally accessible instance of the Manager ---
GM = GameManager()
