"""
Handles all entity-based actions and animations like movement and attacks
"""

from scripts.animation import InterpolationAnimation
from scripts.game_manager import GM


def move_player(player, new_grid_x, new_grid_y, duration_frames=12, on_complete_callback=None):
    """
    Locks the game and smoothly animates the camera to center on the
    player's new grid position. This is the official move action for the Player.

    Args:
        player: The Player object instance.
        new_grid_x: The player's new X grid position.
        new_grid_y: The player's new Y grid position.
        duration_frames: Animation duration for the camera pan.
        on_complete_callback: Optional callback function to call when animation completes.
    """
    # --- Use CURRENT visual offset as starting point ---
    start_visual_x = player.offset_x_visual
    start_visual_y = player.offset_y_visual

    # --- DON'T update grid position yet - wait for animation to complete ---
    player.is_moving = True

    # --- Calculate camera target ---
    player_pixel_x = new_grid_x * GM.render_tile_size
    player_pixel_y = new_grid_y * GM.render_tile_size
    target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
    target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

    # --- Animation complete callback ---
    def on_movement_complete():
        # --- Explicitly set final values to avoid any floating point drift ---
        player.offset_x_visual = float(new_grid_x)
        player.offset_y_visual = float(new_grid_y)
        player.grid_x = new_grid_x
        player.grid_y = new_grid_y
        player.is_moving = False
        if on_complete_callback:
            on_complete_callback()

    # --- Animate visual offset (for sprite sliding) ---
    player_visual_x_anim = InterpolationAnimation(
        target_object=player,
        property_name='offset_x_visual',
        start_value=start_visual_x,
        end_value=float(new_grid_x),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad,
        on_complete_callback=on_movement_complete
    )

    player_visual_y_anim = InterpolationAnimation(
        target_object=player,
        property_name='offset_y_visual',
        start_value=start_visual_y,
        end_value=float(new_grid_y),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_out_quad
    )

    # --- Animate camera (for world scrolling) ---
    GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=duration_frames)

    # --- Add player visual animations ---
    GM.add_animation(player_visual_x_anim)
    GM.add_animation(player_visual_y_anim)

    return player_visual_x_anim


def move_entity(entity, target_grid_x, target_grid_y, duration_frames=12, on_complete_callback=None):
    """
    Smoothly animates an entity from current grid position to target grid position
    by animating the internal slide properties.
    """
    # --- FIXED: Validate that we're actually moving ---
    if entity.grid_x == target_grid_x and entity.grid_y == target_grid_y:
        print(
            f"[ENTITY DEBUG] Entity already at target position ({target_grid_x}, {target_grid_y}), skipping animation")
        if on_complete_callback:
            on_complete_callback()
        return None

    entity.slide_x = 0.0
    entity.slide_y = 0.0
    # --- Store the current position as the start for the animation ---
    entity.start_grid_x, entity.start_grid_y = entity.get_grid_pos()
    entity.is_moving = True

    # --- Calculate the direction and magnitude of the slide ---
    slide_dx = target_grid_x - entity.start_grid_x
    slide_dy = target_grid_y - entity.start_grid_y

    print(
        f"[ENTITY DEBUG] Moving entity from ({entity.start_grid_x}, {entity.start_grid_y}) to ({target_grid_x}, {target_grid_y}), slide: ({slide_dx}, {slide_dy})")

    def finalize_move():
        # --- Update logical grid position ---
        entity.grid_x = target_grid_x
        entity.grid_y = target_grid_y

        # --- Update start positions to match new grid position ---
        entity.start_grid_x = target_grid_x
        entity.start_grid_y = target_grid_y

        # --- Reset animation state ---
        entity.is_moving = False
        entity.slide_x = 0.0
        entity.slide_y = 0.0

        if on_complete_callback:
            on_complete_callback()

    # --- Create Slide Animation ---
    offset_x_animation = InterpolationAnimation(
        target_object=entity,
        property_name='slide_x',
        start_value=0.0,
        end_value=float(slide_dx),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_in_out_quad,
        on_complete_callback=finalize_move
    )

    offset_y_animation = InterpolationAnimation(
        target_object=entity,
        property_name='slide_y',
        start_value=0.0,
        end_value=float(slide_dy),
        duration_frames=duration_frames,
        easing_function=InterpolationAnimation.ease_in_out_quad
    )

    # --- Execute ---
    GM.add_animation(offset_x_animation)
    GM.add_animation(offset_y_animation)

    return offset_x_animation


def move_player_path(player, path, duration_per_tile=8, delay_between_steps=6, on_complete_callback=None):
    """
    Moves the player along a path, animating each step sequentially.

    Args:
        player: The Player object instance.
        path: List of (x, y) tuples representing the path to follow.
        duration_per_tile: Animation duration for each tile movement.
        delay_between_steps: Frames to wait between steps (for unsquish).
        on_complete_callback: Optional callback function to call when all movement completes.
    """
    if not path or len(path) <= 1:
        if on_complete_callback:
            on_complete_callback()
        return

    # --- Start from index 1 (skip current position if it's in the path) ---
    current_index = 0
    if path[0] == (player.grid_x, player.grid_y):
        current_index = 1

    def move_next_step():
        nonlocal current_index

        if current_index >= len(path):
            # --- All steps complete ---
            if on_complete_callback:
                on_complete_callback()
            return

        next_x, next_y = path[current_index]
        current_index += 1

        # --- Determine squash direction for this step ---
        if next_x != player.grid_x:
            player.squash_y = 1.1
            player.squash_x = 0.9
        else:
            player.squash_x = 1.1
            player.squash_y = 0.9

        # --- Callback after movement complete, with delay before next step ---
        def on_step_complete():
            # --- Reset squash ---
            player.squash_x = 1.0
            player.squash_y = 1.0

            # --- Ensure at least 2 frames of delay to render at exact position ---
            actual_delay = max(2, delay_between_steps)  # Minimum 2 frames

            # --- Use the new DelayAnimation class ---
            from scripts.animation import DelayAnimation
            delay_anim = DelayAnimation(actual_delay, move_next_step)
            GM.add_animation(delay_anim)

        # --- Move to next tile ---
        move_player(
            player=player,
            new_grid_x=next_x,
            new_grid_y=next_y,
            duration_frames=duration_per_tile,
            on_complete_callback=on_step_complete
        )

    # --- Start the chain ---
    move_next_step()
