from __future__ import annotations
from blob_physics.vec2 import Vec2


class PointMass:
    __slots__ = ("pos", "old_pos", "mass", "force", "pinned")

    def __init__(self, pos: Vec2, mass: float = 1.0, pinned: bool = False) -> None:
        self.pos = pos.copy()
        self.old_pos = pos.copy()
        self.mass = mass
        self.force = Vec2(0.0, 0.0)
        self.pinned = pinned

    @property
    def velocity(self) -> Vec2:
        return self.pos - self.old_pos

    def add_force(self, f: Vec2) -> None:
        self.force += f

    def clear_force(self) -> None:
        self.force = Vec2(0.0, 0.0)

    def integrate(self, dt: float) -> None:
        if self.pinned:
            return
        acc = self.force * (1.0 / self.mass)
        new_pos = self.pos * 2.0 - self.old_pos + acc * (dt * dt)
        self.old_pos = self.pos.copy()
        self.pos = new_pos
