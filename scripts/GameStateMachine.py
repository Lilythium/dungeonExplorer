from statemachine import StateMachine, State

from statemachine import StateMachine, State


class GameState(StateMachine):
    # --- States ---
    start_screen = State(initial=True)
    player_turn = State()
    player_animating = State()
    enemy_turn = State()
    enemy_animating = State()
    pause_screen = State()
    game_over = State()

    # --- Transitions ---
    start_game = start_screen.to(player_turn)
    player_action = player_turn.to(player_animating)  # Player acts, then their animations play
    player_animations_complete = player_animating.to(enemy_turn)  # Player animations done, enemy turn
    enemy_actions_start = enemy_turn.to(enemy_animating)  # Enemy actions start, then their animations play
    enemy_animations_complete = enemy_animating.to(player_turn)  # Enemy animations done, back to player
    pause_game = player_turn.to(pause_screen) | enemy_turn.to(pause_screen) | player_animating.to(
        pause_screen) | enemy_animating.to(pause_screen)
    unpause_game = (
            pause_screen.to(player_turn, cond="was_player_turn") |
            pause_screen.to(enemy_turn, cond="was_enemy_turn") |
            pause_screen.to(player_animating, cond="was_player_animating") |
            pause_screen.to(enemy_animating, cond="was_enemy_animating")
    )
    game_over_transition = player_turn.to(game_over) | enemy_turn.to(game_over) | player_animating.to(
        game_over) | enemy_animating.to(game_over)

    def __init__(self):
        self.last_state = None
        super().__init__()

    # --- Logic ---
    def on_enter_pause_screen(self, source):
        """This hook runs automatically whenever we enter pause."""
        self.last_state = source.id
        print(f"Paused from: {self.last_state}")

    def was_player_turn(self):
        return self.last_state == "player_turn"

    def was_enemy_turn(self):
        return self.last_state == "enemy_turn"

    def was_player_animating(self):
        return self.last_state == "player_animating"

    def was_enemy_animating(self):
        return self.last_state == "enemy_animating"
