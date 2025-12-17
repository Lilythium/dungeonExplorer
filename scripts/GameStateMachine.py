import pygame
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
    player_action = player_turn.to(player_animating)
    player_animations_complete = player_animating.to(enemy_turn)
    enemy_actions_start = enemy_turn.to(enemy_animating)
    enemy_animations_complete = enemy_animating.to(player_turn)
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
        self.buffered_direction = None  # Store direction as (dx, dy) tuple
        super().__init__()

    # --- Logic ---
    def on_enter_pause_screen(self, source):
        """This hook runs automatically whenever we enter pause."""
        self.last_state = source.id
        print(f"Paused from: {self.last_state}")

    def on_enter_player_turn(self):
        """Called when entering player_turn state."""
        print(f"[STATE] Entered player_turn, buffered direction: {self.buffered_direction}")

    def was_player_turn(self):
        return self.last_state == "player_turn"

    def was_enemy_turn(self):
        return self.last_state == "enemy_turn"

    def was_player_animating(self):
        return self.last_state == "player_animating"

    def was_enemy_animating(self):
        return self.last_state == "enemy_animating"

    def buffer_direction_key(self, event):
        """
        Store a direction key to be processed when returning to player_turn.
        Direction keys are buffered during non-player-turn states.
        """
        # Buffer input during states where player cannot act
        if self.current_state.id in ["player_animating", "enemy_turn", "enemy_animating"]:
            if event.type == pygame.KEYDOWN:
                # Convert key to direction tuple
                direction = self._key_to_direction(event.key)
                if direction:
                    self.buffered_direction = direction
                    print(f"[INPUT BUFFER] Buffered direction: {direction} during {self.current_state.id}")
                    return True
        return False

    def _key_to_direction(self, key):
        """Convert pygame key to direction tuple."""
        if key in [pygame.K_UP, pygame.K_w]:
            return 0, -1
        elif key in [pygame.K_DOWN, pygame.K_s]:
            return 0, 1
        elif key in [pygame.K_LEFT, pygame.K_a]:
            return -1, 0
        elif key in [pygame.K_RIGHT, pygame.K_d]:
            return 1, 0
        return None

    def get_buffered_direction(self):
        """Get and clear the buffered direction."""
        direction = self.buffered_direction
        self.buffered_direction = None
        return direction

    def has_buffered_direction(self):
        """Check if there's a buffered direction."""
        return self.buffered_direction is not None

    @staticmethod
    def update_held_direction():
        """
        Check for held direction keys using pygame.key.get_pressed().
        This should be called at the start of player_turn.
        """
        keys = pygame.key.get_pressed()

        # Check in priority order (right, left, down, up)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return 1, 0
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return -1, 0
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return 0, 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            return 0, -1
        return None
