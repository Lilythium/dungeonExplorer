import random
from typing import List, Tuple, Any

import pygame


class DeathCloudEmitter:
    """
    Manages particles that burst outward from a central point (enemy death).
    """

    def __init__(self, color: Tuple[int, int, int] = (220, 220, 220)):
        # Particle structure: [[x, y], radius, [velocity_x, velocity_y]]
        self.particles: List[List[Any]] = []
        self.base_color = color
        self.max_initial_radius = 8
        self.max_burst_particles = 10
        self.life_decay_rate = 0.5

    def burst(self, start_pos: Tuple[float, float], num_particles: int = None):
        """
        Creates a burst of particles when an enemy dies at start_pos.
        """
        if num_particles is None:
            num_particles = self.max_burst_particles

        for _ in range(num_particles):
            pos_x = start_pos[0]
            pos_y = start_pos[1]

            radius = random.randint(3, self.max_initial_radius)

            velocity_x = random.uniform(-2.0, 2.0)
            velocity_y = random.uniform(-2.0, 2.0)

            # Structure: [[pos_x, pos_y], radius, [velocity_x, velocity_y]]
            particle_circle = [[pos_x, pos_y], radius, [velocity_x, velocity_y]]
            self.particles.append(particle_circle)

    def update_and_draw(self, surf: pygame.Surface):
        """
        Updates the position and size of all particles and draws them.
        """
        if self.particles:
            self._delete_faded_particles()

            for particle in self.particles:

                # --- Update Position ---
                particle[0][0] += particle[2][0]
                particle[0][1] += particle[2][1]

                # --- Update Size (Decay) ---
                particle[1] -= self.life_decay_rate

                # --- Draw the Particle ---
                if particle[1] > 0:
                    pos = (int(particle[0][0]), int(particle[0][1]))

                    pygame.draw.circle(
                        surf,
                        self.base_color,
                        pos,
                        int(particle[1])
                    )

    def _delete_faded_particles(self):
        """
        Removes particles whose radius has shrunk to zero or less.
        """
        # particle[1] is the radius
        particle_copy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particle_copy
