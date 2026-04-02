from __future__ import annotations
import math
from blob_physics.vec2 import Vec2
from blob_physics.point_mass import PointMass
from blob_physics.spring import Spring


class BlobBody:
    def __init__(
        self,
        center: tuple[float, float] = (400, 300),
        radius: float = 40.0,
        num_points: int = 20,
        mass: float = 1.0,
        spring_k: float = 300.0,
        spring_damping: float = 10.0,
        pressure: float = 50.0,
        surface_tension: float = 0.5,
    ) -> None:
        self.pressure_constant = pressure
        self.surface_tension = surface_tension
        self.points: list[PointMass] = []
        self.structural_springs: list[Spring] = []
        self.cross_springs: list[Spring] = []

        # Create point masses in a ring
        point_mass = mass / num_points
        for i in range(num_points):
            angle = 2.0 * math.pi * i / num_points
            px = center[0] + radius * math.cos(angle)
            py = center[1] + radius * math.sin(angle)
            self.points.append(PointMass(Vec2(px, py), mass=point_mass))

        # Structural springs (adjacent points)
        for i in range(num_points):
            j = (i + 1) % num_points
            self.structural_springs.append(
                Spring(self.points[i], self.points[j], stiffness=spring_k, damping=spring_damping)
            )

        # Cross springs (connect opposite points for internal stiffness)
        for i in range(num_points // 2):
            j = (i + num_points // 2) % num_points
            self.cross_springs.append(
                Spring(self.points[i], self.points[j], stiffness=spring_k * 0.3, damping=spring_damping * 0.5)
            )

        # Store target area (area of the initial circle)
        self._target_area = math.pi * radius * radius

    @property
    def target_area(self) -> float:
        return self._target_area

    @target_area.setter
    def target_area(self, value: float) -> None:
        self._target_area = value

    def centroid(self) -> Vec2:
        cx, cy = 0.0, 0.0
        for p in self.points:
            cx += p.pos.x
            cy += p.pos.y
        n = len(self.points)
        return Vec2(cx / n, cy / n)

    def area(self) -> float:
        """Compute enclosed area using the shoelace formula."""
        a = 0.0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            a += self.points[i].pos.x * self.points[j].pos.y
            a -= self.points[j].pos.x * self.points[i].pos.y
        return abs(a) * 0.5

    def _apply_spring_forces(self) -> None:
        for s in self.structural_springs:
            s.apply_force()
        for s in self.cross_springs:
            s.apply_force()

    def _apply_pressure_forces(self) -> None:
        current_area = self.area()
        if current_area < 1e-6:
            return

        ratio = (self._target_area - current_area) / current_area
        ratio = max(-2.0, min(2.0, ratio))  # clamp to prevent explosions
        pressure = self.pressure_constant * ratio
        n = len(self.points)

        for i in range(n):
            j = (i + 1) % n
            edge = self.points[j].pos - self.points[i].pos
            edge_len = edge.length()
            if edge_len < 1e-12:
                continue
            # Outward normal (assuming CCW winding)
            normal = Vec2(-edge.y, edge.x).normalized()
            force = normal * (pressure * edge_len * 0.5)
            self.points[i].add_force(force)
            self.points[j].add_force(force)

    def _apply_surface_tension(self) -> None:
        n = len(self.points)
        for i in range(n):
            prev_p = self.points[(i - 1) % n]
            curr = self.points[i]
            next_p = self.points[(i + 1) % n]

            to_prev = prev_p.pos - curr.pos
            to_next = next_p.pos - curr.pos

            len_prev = to_prev.length()
            len_next = to_next.length()
            if len_prev < 1e-12 or len_next < 1e-12:
                continue

            to_prev_n = to_prev * (1.0 / len_prev)
            to_next_n = to_next * (1.0 / len_next)

            # Pull toward midpoint of neighbors (smoothing force)
            midpoint = (prev_p.pos + next_p.pos) * 0.5
            toward_mid = midpoint - curr.pos
            curr.add_force(toward_mid * self.surface_tension)

    def accumulate_forces(self) -> None:
        for p in self.points:
            p.clear_force()
        self._apply_spring_forces()
        self._apply_pressure_forces()
        self._apply_surface_tension()

    def integrate(self, dt: float) -> None:
        for p in self.points:
            p.integrate(dt)

    def get_positions(self) -> list[Vec2]:
        return [p.pos.copy() for p in self.points]
