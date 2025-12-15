# animation.py
from enum import Enum
from typing import Any, Callable, Optional


class AnimationType(Enum):
    """Defines the type of animation."""
    FRAME_SEQUENCE = "frame_sequence"  # Cycles through tile frames
    INTERPOLATION = "interpolation"  # Lerps a value over time


class Animation:
    """
    Base class for all animations.
    """

    def __init__(self, duration_frames: int):
        self.duration_frames = duration_frames
        self.current_frame = 0
        self.is_complete = False

    def update(self) -> bool:
        """
        Updates the animation by one frame.
        Returns: True if animation is still running, False if complete.
        """
        if self.is_complete:
            return False

        self.current_frame += 1

        if self.current_frame >= self.duration_frames:
            self.is_complete = True
            self.on_complete()
            return False

        return True

    def on_complete(self):
        """Called when the animation finishes. Override in subclasses."""
        pass

    def get_progress(self) -> float:
        """Returns animation progress from 0.0 to 1.0."""
        if self.duration_frames == 0:
            return 1.0
        return min(1.0, self.current_frame / self.duration_frames)


class FrameSequenceAnimation(Animation):
    """
    Animation that cycles through a sequence of tile indices.
    Used for things like door opening, chest opening, etc.
    """

    def __init__(
            self,
            pos_x: int,
            pos_y: int,
            frame_sequence: list[int],
            duration_frames: int,
            on_complete_callback: Optional[Callable] = None
    ):
        super().__init__(duration_frames)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.frame_sequence = frame_sequence
        self.on_complete_callback = on_complete_callback

        # Calculate frames per tile
        self.frames_per_tile = duration_frames // len(frame_sequence)
        if self.frames_per_tile == 0:
            self.frames_per_tile = 1

    def get_current_tile_id(self) -> int:
        """Returns the current tile ID based on animation progress."""
        if self.is_complete:
            return self.frame_sequence[-1]

        index = min(
            self.current_frame // self.frames_per_tile,
            len(self.frame_sequence) - 1
        )
        return self.frame_sequence[index]

    def on_complete(self):
        """Execute callback when animation completes."""
        if self.on_complete_callback:
            self.on_complete_callback(self.pos_x, self.pos_y, self.frame_sequence[-1])


class InterpolationAnimation(Animation):
    """
    Animation that interpolates (lerps) a value over time.
    Can be used for movement, fading, scaling, etc.
    """

    def __init__(
            self,
            target_object: Any,
            property_name: str,
            start_value: float | tuple,
            end_value: float | tuple,
            duration_frames: int,
            easing_function: Optional[Callable[[float], float]] = None,
            on_complete_callback: Optional[Callable] = None
    ):
        super().__init__(duration_frames)
        self.target_object = target_object
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.easing_function = easing_function or self.linear_ease
        self.on_complete_callback = on_complete_callback

        # Determine if we're interpolating a tuple (like position) or a single value
        self.is_tuple = isinstance(start_value, tuple)

    @staticmethod
    def linear_ease(t: float) -> float:
        """Linear easing function."""
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in."""
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out."""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out."""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2

    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        """Linear interpolation between two values."""
        return start + (end - start) * t

    def update(self) -> bool:
        """Updates the interpolation and sets the new value on the target object."""
        still_running = super().update()
        if self.is_complete:
            eased_progress = 1.0
        else:
            # Get eased progress
            progress = self.get_progress()
            eased_progress = self.easing_function(progress)

        # Calculate and set the new value
        if self.is_tuple:
            new_value = tuple(
                self.lerp(self.start_value[i], self.end_value[i], eased_progress)
                for i in range(len(self.start_value))
            )
        else:
            new_value = self.lerp(self.start_value, self.end_value, eased_progress)

        setattr(self.target_object, self.property_name, new_value)

        return still_running

    def on_complete(self):
        """Ensure final value is set and execute callback."""
        # Set the exact end value
        setattr(self.target_object, self.property_name, self.end_value)

        if self.on_complete_callback:
            self.on_complete_callback()


class AnimationManager:
    """
    Manages all active animations in the game.
    Integrated into the GameManager.
    """

    def __init__(self):
        self.active_animations: list[Animation] = []
        self.is_locked = False

    def add_animation(self, animation: Animation):
        """Add an animation to the active list."""
        self.active_animations.append(animation)
        if not self.is_locked:
            self.is_locked = True

    def update(self) -> bool:
        """
        Updates all active animations.
        Returns: True if any animations are still running.
        """
        if not self.active_animations:
            self.is_locked = False
            return False

        # Update all animations and remove completed ones
        self.active_animations = [
            anim for anim in self.active_animations
            if anim.update()
        ]

        # If no animations remain, unlock
        if not self.active_animations:
            self.is_locked = False
            return False

        return True

    def clear_all(self):
        """Clears all active animations."""
        self.active_animations.clear()
        self.is_locked = False

    def is_animating(self) -> bool:
        """Returns whether any animations are currently active."""
        return len(self.active_animations) > 0
