"""
Enhanced entity_actions.py with multi-tile path movement support
"""

from scripts.animation import InterpolationAnimation
from scripts.game_manager import GM


def move_player_path(player, path, frames_per_tile=10, on_complete_callback=None):
    """
    Animates the player moving along a multi-tile path by moving the camera,
    keeping the player visually centered at all times.

    Args:
        player: The Player object instance
        path: List of (x, y) tuples representing the path to follow
        frames_per_tile: Animation duration for each tile transition
        on_complete_callback: Called when the entire path is complete
    """
    if not path or len(path) < 2:
        if on_complete_callback:
            on_complete_callback()
        return

    # Remove starting position if it's current position
    if path[0] == (player.grid_x, player.grid_y):
        path = path[1:]

    if not path:
        if on_complete_callback:
            on_complete_callback()
        return

    current_step = 0
    total_steps = len(path)

    def animate_next_step():
        """Recursively animates each step in the path."""
        nonlocal current_step

        if current_step >= total_steps:
            # Path complete - ensure visual sync
            player.sync_visual_offset()
            player.is_moving = False
            if on_complete_callback:
                on_complete_callback()
            return

        # Get next destination
        next_x, next_y = path[current_step]

        # Determine squash direction for this step
        if next_x != player.grid_x:
            player.squash_y = 1.1
            player.squash_x = 0.9
        else:
            player.squash_x = 1.1
            player.squash_y = 0.9

        # Store current visual position as animation start
        start_visual_x = player.offset_x_visual
        start_visual_y = player.offset_y_visual

        # Update player's logical position IMMEDIATELY
        player.grid_x = next_x
        player.grid_y = next_y

        # Calculate where the camera needs to be to center the player
        player_pixel_x = next_x * GM.render_tile_size
        player_pixel_y = next_y * GM.render_tile_size
        target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
        target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

        # Increment step counter BEFORE creating animations
        current_step += 1

        # Callback for this step
        def on_step_complete():
            # Reset squash for next step
            player.squash_x = 1.0
            player.squash_y = 1.0

            # Update visual offset to match new grid position
            player.offset_x_visual = float(next_x)
            player.offset_y_visual = float(next_y)

            # Continue to next step
            animate_next_step()

        # Create animations for this step
        player_visual_x_anim = InterpolationAnimation(
            target_object=player,
            property_name='offset_x_visual',
            start_value=start_visual_x,
            end_value=float(next_x),
            duration_frames=frames_per_tile,
            easing_function=InterpolationAnimation.ease_out_quad,
            on_complete_callback=on_step_complete
        )

        player_visual_y_anim = InterpolationAnimation(
            target_object=player,
            property_name='offset_y_visual',
            start_value=start_visual_y,
            end_value=float(next_y),
            duration_frames=frames_per_tile,
            easing_function=InterpolationAnimation.ease_out_quad
        )

        # Animate camera to new position
        GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=frames_per_tile)

        # Add animations
        GM.add_animation(player_visual_x_anim)
        GM.add_animation(player_visual_y_anim)

    # Start the animation chain
    player.is_moving = True
    animate_next_step()


def move_player(player, new_grid_x, new_grid_y, duration_frames=12, on_complete_callback=None):
    """
    Single-tile movement (for compatibility with existing code).
    Locks the game and smoothly animates the camera to center on the
    player's new grid position.
    """
    start_visual_x = player.offset_x_visual
    start_visual_y = player.offset_y_visual

    player.grid_x = new_grid_x
    player.grid_y = new_grid_y
    player.is_moving = True

    player_pixel_x = new_grid_x * GM.render_tile_size
    player_pixel_y = new_grid_y * GM.render_tile_size
    target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
    target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

    def on_movement_complete():
        player.sync_visual_offset()
        player.is_moving = False
        if on_complete_callback:
            on_complete_callback()

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

    GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=duration_frames)

    GM.add_animation(player_visual_x_anim)
    GM.add_animation(player_visual_y_anim)

    return player_visual_x_anim


def move_entity_path(entity, path, frames_per_tile=10, on_complete_callback=None):
    """
    Animates an entity moving along a multi-tile path, creating a separate
    animation for each tile transition.

    Args:
        entity: The Entity object instance
        path: List of (x, y) tuples representing the path to follow
        frames_per_tile: Animation duration for each tile transition
        on_complete_callback: Called when the entire path is complete
    """
    if not path or len(path) < 2:
        if on_complete_callback:
            on_complete_callback()
        return

    # --- Remove the starting position (entity's current location) ---
    if path[0] == (entity.grid_x, entity.grid_y):
        path = path[1:]

    if not path:
        if on_complete_callback:
            on_complete_callback()
        return

    current_step = 0
    total_steps = len(path)

    def animate_next_step():
        """Recursively animates each step in the path."""
        nonlocal current_step

        if current_step >= total_steps:
            # --- Path complete ---
            entity.is_moving = False
            entity.slide_x = 0.0
            entity.slide_y = 0.0
            entity.start_grid_x = entity.grid_x
            entity.start_grid_y = entity.grid_y
            if on_complete_callback:
                on_complete_callback()
            return

        # --- Get next destination ---
        next_x, next_y = path[current_step]

        # --- Store current position as start ---
        entity.start_grid_x = entity.grid_x
        entity.start_grid_y = entity.grid_y

        # --- Calculate slide distance ---
        slide_dx = next_x - entity.start_grid_x
        slide_dy = next_y - entity.start_grid_y

        # --- Determine squash direction for this step ---
        if slide_dx != 0:
            entity.squash_y = 1.1
            entity.squash_x = 0.9
        else:
            entity.squash_x = 1.1
            entity.squash_y = 0.9

        # --- Update entity's logical position ---
        entity.grid_x = next_x
        entity.grid_y = next_y

        # --- Callback for this step ---
        def on_step_complete():
            # --- Reset slide and squash for next step ---
            entity.slide_x = 0.0
            entity.slide_y = 0.0
            entity.squash_x = 1.0
            entity.squash_y = 1.0
            entity.start_grid_x = next_x
            entity.start_grid_y = next_y
            animate_next_step()

        # --- Increment step counter ---
        current_step += 1

        # --- Create animations for this step ---
        offset_x_animation = InterpolationAnimation(
            target_object=entity,
            property_name='slide_x',
            start_value=0.0,
            end_value=float(slide_dx),
            duration_frames=frames_per_tile,
            easing_function=InterpolationAnimation.ease_out_quad,
            on_complete_callback=on_step_complete
        )

        offset_y_animation = InterpolationAnimation(
            target_object=entity,
            property_name='slide_y',
            start_value=0.0,
            end_value=float(slide_dy),
            duration_frames=frames_per_tile,
            easing_function=InterpolationAnimation.ease_out_quad
        )

        # --- Add animations ---
        GM.add_animation(offset_x_animation)
        GM.add_animation(offset_y_animation)

    # --- Start the animation chain ---
    entity.is_moving = True
    entity.slide_x = 0.0
    entity.slide_y = 0.0
    animate_next_step()


def move_entity(entity, target_grid_x, target_grid_y, duration_frames=12, on_complete_callback=None):
    """Smoothly animates an entity from current grid position to target grid position."""
    if entity.grid_x == target_grid_x and entity.grid_y == target_grid_y:
        print(
            f"[ENTITY DEBUG] Entity already at target position ({target_grid_x}, {target_grid_y}), skipping animation")
        if on_complete_callback:
            on_complete_callback()
        return None

    # --- Store current position as animation start ---
    entity.start_grid_x = entity.grid_x
    entity.start_grid_y = entity.grid_y
    entity.slide_x = 0.0
    entity.slide_y = 0.0
    entity.is_moving = True

    # --- Calculate slide distance ---
    slide_dx = target_grid_x - entity.start_grid_x
    slide_dy = target_grid_y - entity.start_grid_y

    # --- Update logical position immediately ---
    entity.grid_x = target_grid_x
    entity.grid_y = target_grid_y

    print(
        f"[ENTITY DEBUG] Moving entity from ({entity.start_grid_x}, {entity.start_grid_y}) to ({target_grid_x}, {target_grid_y}), slide: ({slide_dx}, {slide_dy})")

    def finalize_move():
        entity.start_grid_x = target_grid_x
        entity.start_grid_y = target_grid_y
        entity.is_moving = False
        entity.slide_x = 0.0
        entity.slide_y = 0.0

        if on_complete_callback:
            on_complete_callback()

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

    GM.add_animation(offset_x_animation)
    GM.add_animation(offset_y_animation)

    return offset_x_animation
