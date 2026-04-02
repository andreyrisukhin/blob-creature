from __future__ import annotations
from blob_physics.vec2 import Vec2
from blob_physics.blob_body import BlobBody
from blob_physics.collision import point_vs_segment, point_vs_bounds


class BlobWorld:
    def __init__(
        self,
        gravity: tuple[float, float] = (0.0, 400.0),
        bounds: tuple[float, float] | None = (800, 600),
    ) -> None:
        self.gravity = Vec2(*gravity)
        self.bounds = bounds
        self.blobs: list[BlobBody] = []
        self.terrain: list[tuple[Vec2, Vec2]] = []  # list of (start, end) segments

    def add_blob(self, blob: BlobBody) -> None:
        self.blobs.append(blob)

    def add_terrain_segment(self, a: tuple[float, float], b: tuple[float, float]) -> None:
        self.terrain.append((Vec2(*a), Vec2(*b)))

    def step(self, dt: float) -> None:
        for blob in self.blobs:
            # Accumulate internal forces
            blob.accumulate_forces()

            # Apply gravity
            for p in blob.points:
                p.add_force(self.gravity * p.mass)

            # Integrate
            blob.integrate(dt)

            # Collision with terrain
            for p in blob.points:
                for seg_a, seg_b in self.terrain:
                    point_vs_segment(p, seg_a, seg_b)

            # Collision with bounds
            if self.bounds:
                for p in blob.points:
                    point_vs_bounds(p, self.bounds[0], self.bounds[1])
