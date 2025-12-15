"""
Handles all level-based actions and animations like doors, chests, fountains, etc.
"""
from scripts.animation import FrameSequenceAnimation
from scripts.tileset import Tile
from scripts.game_manager import GM


class LevelActions:
    """
    Contains all the action handlers for level interactions.
    Each method creates and returns an animation.
    """

    def __init__(self, level):
        """
        Args:
            level: Reference to the Level instance
        """
        self.level = level

    def open_door_small(self, pos_x, pos_y):
        """Opens a small door with animation."""

        frame_sequence = [
            Tile.DOOR_SMALL_CLOSED.value,
            Tile.DOOR_SMALL_OPENING.value,
            Tile.DOOR_SMALL_OPENED.value
        ]

        def on_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]

        animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES,
            on_complete_callback=on_complete
        )

        self.level.animated_tiles[(pos_x, pos_y)] = animation
        GM.add_animation(animation)

        print(f"Small door at ({pos_x}, {pos_y}) opening.")
        return True

    def open_door_left(self, pos_x, pos_y, doRecurse=True):
        """Opens a left door with animation."""

        if doRecurse:
            self.open_door_right(pos_x + 1, pos_y, False)

        frame_sequence = [
            Tile.DOOR_LEFT_CLOSED.value,
            Tile.DOOR_LEFT_OPENING.value,
            Tile.DOOR_LEFT_OPENED.value
        ]

        def on_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]

        animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES,
            on_complete_callback=on_complete
        )

        self.level.animated_tiles[(pos_x, pos_y)] = animation
        GM.add_animation(animation)

        print(f"Left door at ({pos_x}, {pos_y}) opening.")
        return True

    def open_door_right(self, pos_x, pos_y, doRecurse=True):
        """Opens a right door with animation."""

        if doRecurse:
            self.open_door_right(pos_x - 1, pos_y, False)

        frame_sequence = [
            Tile.DOOR_RIGHT_CLOSED.value,
            Tile.DOOR_RIGHT_OPENING.value,
            Tile.DOOR_RIGHT_OPENED.value
        ]

        def on_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]

        animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES,
            on_complete_callback=on_complete
        )

        self.level.animated_tiles[(pos_x, pos_y)] = animation
        GM.add_animation(animation)

        print(f"Right door at ({pos_x}, {pos_y}) opening.")
        return True

    def open_chest(self, pos_x, pos_y):
        """Opens a chest with animation."""
        # TODO: add chance to replace opened chess with mimic instead
        frame_sequence = [
            Tile.CHEST_CLOSED.value,
            Tile.CHEST_OPENING.value,
            Tile.CHEST_OPENED.value
        ]

        def on_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]
            # TODO: Add loot drop logic here
            print(f"Chest opened! Add loot generation here.")

        animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES,
            on_complete_callback=on_complete
        )

        self.level.animated_tiles[(pos_x, pos_y)] = animation
        GM.add_animation(animation)

        print(f"Chest at ({pos_x}, {pos_y}) opening.")
        return True

    def activate_fountain(self, pos_x, pos_y, tile_id):
        """Toggles fountain on/off with animation (both top and bottom)."""

        if tile_id == Tile.FOUNTAIN_BOTTOM_OFF.value:
            bottom_frame_sequence = [
                Tile.FOUNTAIN_BOTTOM_OFF.value,
                Tile.FOUNTAIN_BOTTOM_ON.value
            ]
            top_frame_sequence = [
                Tile.FOUNTAIN_TOP_OFF_GARGOYLE.value,
                Tile.FOUNTAIN_TOP_ON_GARGOYLE.value
            ]
            action = "activating"
        elif tile_id == Tile.FOUNTAIN_BOTTOM_ON.value:
            bottom_frame_sequence = [
                Tile.FOUNTAIN_BOTTOM_ON.value,
                Tile.FOUNTAIN_BOTTOM_OFF.value
            ]
            top_frame_sequence = [
                Tile.FOUNTAIN_TOP_ON_GARGOYLE.value,
                Tile.FOUNTAIN_TOP_OFF_GARGOYLE.value
            ]
            action = "deactivating"
        elif tile_id == Tile.FOUNTAIN_BOTTOM_OFF_GRATE.value:
            bottom_frame_sequence = [
                Tile.FOUNTAIN_BOTTOM_OFF_GRATE.value,
                Tile.FOUNTAIN_BOTTOM_ON_GRATE.value
            ]
            top_frame_sequence = [
                Tile.FOUNTAIN_TOP_OFF_GARGOYLE.value,
                Tile.FOUNTAIN_TOP_ON_GARGOYLE.value
            ]
            action = "activating"
        elif tile_id == Tile.FOUNTAIN_BOTTOM_ON_GRATE.value:
            bottom_frame_sequence = [
                Tile.FOUNTAIN_BOTTOM_ON_GRATE.value,
                Tile.FOUNTAIN_BOTTOM_OFF_GRATE.value
            ]
            top_frame_sequence = [
                Tile.FOUNTAIN_TOP_ON_GARGOYLE.value,
                Tile.FOUNTAIN_TOP_OFF_GARGOYLE.value
            ]
            action = "deactivating"
        else:
            return False

        # Create callback for bottom that also removes from animated tiles
        def on_bottom_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]

        # Create callback for top that also removes from animated tiles
        def on_top_complete(x, y, final_id):
            self.level.set_tile_at(x, y, final_id)
            pos_key = (x, y)
            if pos_key in self.level.animated_tiles:
                del self.level.animated_tiles[pos_key]

        # Create animation for BOTTOM (the tile that was clicked)
        bottom_animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=pos_y,
            frame_sequence=bottom_frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES // 2,  # Faster toggle
            on_complete_callback=on_bottom_complete
        )

        # Create animation for TOP (one tile above)
        top_pos_y = pos_y - 1
        top_animation = FrameSequenceAnimation(
            pos_x=pos_x,
            pos_y=top_pos_y,
            frame_sequence=top_frame_sequence,
            duration_frames=GM.ANIMATION_DELAY_FRAMES // 2,  # Same duration
            on_complete_callback=on_top_complete
        )

        # Track both tiles as animated
        self.level.animated_tiles[(pos_x, pos_y)] = bottom_animation
        self.level.animated_tiles[(pos_x, top_pos_y)] = top_animation

        # Add both animations to the manager
        GM.add_animation(bottom_animation)
        GM.add_animation(top_animation)

        print(f"Fountain at ({pos_x}, {pos_y}) {action}")
        return True
