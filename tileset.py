from enum import Enum


class Tile(Enum):
    EMPTY = -1
    # --- TILES ---
    # Internal walls
    INTERNAL_WALL_0 = 0
    INTERNAL_WALL_1 = 12
    INTERNAL_WALL_2 = 24

    # Exposed walls
    EXPOSED_WALL_RIGHT = 13
    EXPOSED_WALL_LEFT = 15
    EXPOSED_WALL_BOTTOM_RIGHT = 25
    EXPOSED_WALL_TOP = 26
    EXPOSED_WALL_BOTTOM_LEFT = 27
    EXPOSED_WALL_TOP_RIGHT = 1
    EXPOSED_WALL_BOTTOM = 2
    EXPOSED_WALL_BOTTOM_BASE = 14
    EXPOSED_WALL_TOP_LEFT = 3

    # Stairs
    WIDE_STAIR_LEFT = 36
    WIDE_STAIR_MID = 37
    WIDE_STAIR_RIGHT = 38
    THIN_STAIR = 39

    # Doors
    DOOR_SMALL = 9
    DOOR_LEFT = 10
    DOOR_RIGHT = 11
    DOOR_SMALL_OPENED = 21
    DOOR_LEFT_OPENED = 22
    DOOR_RIGHT_OPENED = 23
    DOOR_SMALL_OPENING = 33
    DOOR_LEFT_OPENING = 34
    DOOR_RIGHT_OPENING = 35
    DOOR_SMALL_CLOSED = 45
    DOOR_LEFT_CLOSED = 46
    DOOR_RIGHT_CLOSED = 47

    # Pillar
    PILLAR_TOP = 6
    PILLAR_MID = 18
    PILLAR_BASE = 30

    # Fountains
    FOUNTAIN_TOP_OFF = 7
    FOUNTAIN_TOP_ON = 8
    FOUNTAIN_TOP_OFF_GARGOYLE = 19
    FOUNTAIN_TOP_ON_GARGOYLE = 20

    FOUNTAIN_BOTTOM_OFF = 31
    FOUNTAIN_BOTTOM_ON = 32
    FOUNTAIN_BOTTOM_OFF_GRATE = 43
    FOUNTAIN_BOTTOM_ON_GRATE = 44

    # Ground
    GROUND = 48
    GROUND_SPECKLED = 49
    GROUND_STONES = 42
    GROUND_SPIKES = 41

    # Misc
    CHEST_CLOSED = 89
    CHEST_OPENING = 90
    CHEST_OPENED = 91
    CHEST_MIMIC = 92

    BARREL = 82
    TABLE = 72
    STOOL = 73
    ANVIL = 74

    BOX_TOP = 63
    BOX_BASE = 75

    TOMBSTONE = 64
    TOMBSTONE_ALT = 65
    MOUND_OF_DIRT = 66

    # --- ENTITIES ---
    PLAYER_CHARACTER = 99

    # Enemies
    GHOST_SMALL = 108
    GHOST_LARGE = 121
    CYCLOPS = 109
    CRAB = 110
    SORCERER = 111
    BAT = 120
    SPIDER = 122
    RAT_BROWN = 123
    RAT_GREY = 124
    DWARF = 87

    # --- UX ---
    SELECTOR = 60
    DANGER_INDICATOR = 61
    ATTACK_INDICATOR = 62

    # --- Static Sets ---

    @staticmethod
    def get_walkable_tiles():
        """Returns a set of integer indices for all tiles the player can walk onto."""
        return {
            Tile.GROUND.value,
            Tile.GROUND_SPECKLED.value,
            Tile.GROUND_STONES.value,
            Tile.GROUND_SPIKES.value,
            Tile.WIDE_STAIR_LEFT.value,
            Tile.WIDE_STAIR_MID.value,
            Tile.WIDE_STAIR_RIGHT.value,
            Tile.THIN_STAIR.value,
        }


def tile(_tile):
    return str(_tile.value)
