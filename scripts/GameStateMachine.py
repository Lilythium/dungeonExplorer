from statemachine import StateMachine, State


class GameState(StateMachine):
    # --- States ---
    start_screen = State(initial=True)
    player_movement_phase = State()
    player_action_phase = State()
    enemy_turn = State()
    pause_screen = State()
    game_over = State(final=True)  # Add final=True to indicate it's a terminal state

    # --- Transitions ---
    start_game = start_screen.to(player_movement_phase)

    # Player turn flow: movement -> action -> enemy turn
    player_movement_complete = player_movement_phase.to(player_action_phase)
    player_has_no_action = player_movement_phase.to(enemy_turn)
    player_action_complete = player_action_phase.to(enemy_turn)
    player_skip_action = player_action_phase.to(enemy_turn)  # Skip action phase

    # Enemy turn flow
    enemy_turn_complete = enemy_turn.to(player_movement_phase)

    # Pause handling
    pause_game = (
            player_movement_phase.to(pause_screen) |
            player_action_phase.to(pause_screen) |
            enemy_turn.to(pause_screen)
    )
    unpause_game = (
            pause_screen.to(player_movement_phase, cond="was_player_movement") |
            pause_screen.to(player_action_phase, cond="was_player_action") |
            pause_screen.to(enemy_turn, cond="was_enemy_turn")
    )

    # Game over
    game_over_transition = (
            player_movement_phase.to(game_over) |
            player_action_phase.to(game_over) |
            enemy_turn.to(game_over)
    )

    def __init__(self):
        self.last_state = None
        self.animations_running = False  # Track if any animations are running
        self.enemy_turn_processed = False  # Initialize here
        super().__init__()

    def on_enter_enemy_turn(self):
        """Called when entering enemy turn state."""
        print("[STATE] Entering enemy turn")
        # Reset the processing flag
        self.enemy_turn_processed = False

    def on_enter_pause_screen(self, source):
        """This hook runs automatically whenever we enter pause."""
        self.last_state = source.id
        print(f"Paused from: {self.last_state}")

    def was_player_movement(self):
        return self.last_state == "player_movement_phase"

    def was_player_action(self):
        return self.last_state == "player_action_phase"

    def was_enemy_turn(self):
        return self.last_state == "enemy_turn"
