"""
Handles all entity-based actions and animations like movement and attacks
"""


class EntityActions:
    """
    Contains all the action handlers for entity interactions.
    Each method creates and returns an animation.
    """

    def __init__(self):
        # might need to pass reference to the entity layer here?
        pass

    def move_player(self, player, new_grid_x, new_grid_y, duration_frames=12):
        """
        Locks the game and smoothly animates the camera to center on the
        player's new grid position. This is the official move action for the Player.

        Args:
            player: The Player object instance.
            new_grid_x: The player's new X grid position (already set on the player).
            new_grid_y: The player's new Y grid position (already set on the player).
            duration_frames: Animation duration for the camera pan.
        """
        from game_manager import GM

        if duration_frames is None:
            duration_frames = GM.ANIMATION_DELAY_FRAMES // 2

        player_pixel_x = new_grid_x * GM.render_tile_size
        player_pixel_y = new_grid_y * GM.render_tile_size

        target_offset_x = GM.screen_width // 2 - player_pixel_x - (GM.render_tile_size // 2)
        target_offset_y = GM.screen_height // 2 - player_pixel_y - (GM.render_tile_size // 2)

        GM.current_level.animate_camera_to(target_offset_x, target_offset_y, duration_frames=duration_frames)

    def move_entity(self, entity, target_offset_x, target_offset_y, duration_frames=20):
        """
        Smoothly animates an entity from current grid position to target grid position.
        """
        from game_manager import GM
        from animation import InterpolationAnimation

        # Store the starting grid position
        start_grid_x, start_grid_y = entity.get_grid_pos()

        # Store target for animation (these are the final grid coordinates)
        target_grid_x = target_offset_x
        target_grid_y = target_offset_y

        def finalize_move():
            entity.set_grid_pos(target_grid_x, target_grid_y)
            entity.sync_visual_offset()  # Ensure O_v == G_x
            entity.is_moving = False

        # We must lock the game loop during entity movement animation
        GM.is_locked = True
        entity.is_moving = True
        # --- Create animation for grid_x ---
        offset_x_animation = InterpolationAnimation(
            target_object=entity,
            property_name='offset_x_visual',  # Assuming a visual offset property for animation
            start_value=start_grid_x,
            end_value=target_grid_x,
            duration_frames=duration_frames,
            easing_function=InterpolationAnimation.linear_ease,
            on_complete_callback=finalize_move
        )

        # --- Create animation for grid_y ---
        offset_y_animation = InterpolationAnimation(
            target_object=entity,
            property_name='offset_y_visual',
            start_value=start_grid_y,
            end_value=target_grid_y,
            duration_frames=duration_frames,
            easing_function=InterpolationAnimation.linear_ease
        )

        # Add both animations
        GM.add_animation(offset_x_animation)
        GM.add_animation(offset_y_animation)

        # Note: Since the player is centered, this movement animation is tricky.
        # A simpler way for a centered player is to use this function to just lock
        # the game and let the camera movement handle the visual update.
        # But for non-centered entities (like enemies), this structure is correct.
