"""
Handles all entity-based actions and animations like movement and attacks
"""

from scripts.animation import InterpolationAnimation
from scripts.game_manager import GM


class EntityActions:
    """
    Contains all the action handlers for entity interactions.
    Each method creates and returns an animation.
    """

    def __init__(self):
        pass


def move_player(player, new_grid_x, new_grid_y, duration_frames=12):
    """
    Locks the game and smoothly animates the camera to center on the
    player's new grid position. This is the official move action for the Player.

    Args:
        player: The Player object instance.
        new_grid_x: The player's new X grid position (already set on the player).
        new_grid_y: The player's new Y grid position (already set on the player).
        duration_frames: Animation duration for the camera pan.
    """

    start_visual_x = player.offset_x_visual
    start_visual_y = player.offset_y_visual

    # Update the player's logical grid position immediately
    player.grid_x = new_grid_x
    player.grid_y = new_grid_y
    player.is_moving = True

    # Calculate camera target
    player_pixel_x = new_grid_x * GM.render_tile_size
    player_pixel_y = new_grid_y * GM.render_tile_size
    target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
    target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

    # Animation complete callback
    def on_movement_complete():
        player.sync_visual_offset()
        player.is_moving = False

    # --- Animate visual offset (for sprite sliding) ---
    player_visual_x_anim = InterpolationAnimation(
        target_object=player,
        property_name='offset_x_visual',
        start_value=start_visual_x,  # Use current visual position
        end_value=float(new_grid_x),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad,
        on_complete_callback=on_movement_complete
    )

    player_visual_y_anim = InterpolationAnimation(
        target_object=player,
        property_name='offset_y_visual',
        start_value=start_visual_y,  # Use current visual position
        end_value=float(new_grid_y),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad
    )

    # --- Animate camera (for world scrolling) ---
    GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=duration_frames)

    # Add player visual animations
    GM.add_animation(player_visual_x_anim)
    GM.add_animation(player_visual_y_anim)

    print(f"Player moving to ({new_grid_x}, {new_grid_y}) from visual offset ({start_visual_x}, {start_visual_y})")


def move_entity(entity, target_grid_x, target_grid_y, duration_frames=12):
    """
    Smoothly animates an entity from current grid position to target grid position
    by animating the internal slide properties.
    """
    entity.slide_x = 0.0
    entity.slide_y = 0.0
    # Store the current position as the start for the animation
    entity.start_grid_x, entity.start_grid_y = entity.get_grid_pos()
    entity.is_moving = True

    # Calculate the direction and magnitude of the slide
    slide_dx = target_grid_x - entity.start_grid_x
    slide_dy = target_grid_y - entity.start_grid_y

    print(f"[MOVE DEBUG] Entity at ({entity.grid_x}, {entity.grid_y}) moving to ({target_grid_x}, {target_grid_y})")
    print(f"[MOVE DEBUG] Slide delta: ({slide_dx}, {slide_dy})")
    print(f"[MOVE DEBUG] Starting slide values: ({entity.slide_x}, {entity.slide_y})")

    def finalize_move():
        print(f"[MOVE DEBUG] Finalizing move - current slide: ({entity.slide_x}, {entity.slide_y})")

        # Update logical grid position
        entity.grid_x = target_grid_x
        entity.grid_y = target_grid_y

        # Update start positions to match new grid position
        entity.start_grid_x = target_grid_x
        entity.start_grid_y = target_grid_y

        # Reset animation state
        entity.is_moving = False
        entity.slide_x = 0.0
        entity.slide_y = 0.0

        print(
            f"[MOVE DEBUG] Move finalized - grid: ({entity.grid_x}, {entity.grid_y}), slide: ({entity.slide_x}, {entity.slide_y})")

    # --- Create Slide Animation ---
    offset_x_animation = InterpolationAnimation(
        target_object=entity,
        property_name='slide_x',
        start_value=0.0,
        end_value=float(slide_dx),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad,
        on_complete_callback=finalize_move
    )

    offset_y_animation = InterpolationAnimation(
        target_object=entity,
        property_name='slide_y',
        start_value=0.0,
        end_value=float(slide_dy),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad
    )

    # Execute
    GM.add_animation(offset_x_animation)
    GM.add_animation(offset_y_animation)

    return offset_x_animation

