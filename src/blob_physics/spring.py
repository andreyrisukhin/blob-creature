from __future__ import annotations
from blob_physics.point_mass import PointMass
from blob_physics.vec2 import Vec2


class Spring:
    __slots__ = ("a", "b", "rest_length", "stiffness", "damping")

    def __init__(
        self,
        a: PointMass,
        b: PointMass,
        rest_length: float | None = None,
        stiffness: float = 300.0,
        damping: float = 10.0,
    ) -> None:
        self.a = a
        self.b = b
        self.rest_length = rest_length if rest_length is not None else a.pos.distance_to(b.pos)
        self.stiffness = stiffness
        self.damping = damping

    def apply_force(self) -> None:
        delta = self.b.pos - self.a.pos
        dist = delta.length()
        if dist < 1e-12:
            return

        direction = delta * (1.0 / dist)
        stretch = dist - self.rest_length

        # Hooke's law
        force_magnitude = self.stiffness * stretch

        # Damping along spring axis
        relative_vel = self.b.velocity - self.a.velocity
        damping_force = self.damping * relative_vel.dot(direction)

        total = (force_magnitude + damping_force)
        force = direction * total

        self.a.add_force(force)
        self.b.add_force(-force)
