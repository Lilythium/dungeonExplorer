# game_manager.py

class GameManager:
    """
    Holds the single, authoritative instances of key game objects
    (Level, Player) for easy global access throughout the game.
    """

    # Static variable to hold the single instance of the manager
    _instance = None

    def __new__(cls):
        """Ensures only one instance of GameManager can be created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
            # Initialize attributes on the first call
            cls._instance.current_level = None
            cls._instance.player = None
            cls._instance.render_tile_size = 0
            cls._instance.screen_width = 0
            cls._instance.screen_height = 0
            # Add other global objects like EnemyHandler, UIController here later
        return cls._instance

    def handle_turn(self):
        """
        Processes a full game turn: Player action, then Entity actions.
        This is typically called after the player confirms a move or attack.
        """


GM = GameManager()
