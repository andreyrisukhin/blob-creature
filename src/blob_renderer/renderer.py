from __future__ import annotations
import math
import pygame
from blob_physics.vec2 import Vec2
from blob_physics.blob_body import BlobBody


def catmull_rom_points(positions: list[Vec2], subdivisions: int = 4) -> list[tuple[int, int]]:
    """Generate smooth curve through blob points using Catmull-Rom interpolation."""
    n = len(positions)
    if n < 3:
        return [(int(p.x), int(p.y)) for p in positions]

    result: list[tuple[int, int]] = []
    for i in range(n):
        p0 = positions[(i - 1) % n]
        p1 = positions[i]
        p2 = positions[(i + 1) % n]
        p3 = positions[(i + 2) % n]

        for s in range(subdivisions):
            t = s / subdivisions
            t2 = t * t
            t3 = t2 * t

            x = 0.5 * (
                (2 * p1.x)
                + (-p0.x + p2.x) * t
                + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2
                + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3
            )
            y = 0.5 * (
                (2 * p1.y)
                + (-p0.y + p2.y) * t
                + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2
                + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3
            )
            result.append((int(x), int(y)))

    return result


def draw_blob(surface: pygame.Surface, blob: BlobBody, color: tuple[int, int, int] = (80, 200, 120)) -> None:
    """Draw blob as a smooth filled shape."""
    positions = blob.get_positions()
    smooth = catmull_rom_points(positions, subdivisions=4)
    if len(smooth) >= 3:
        pygame.draw.polygon(surface, color, smooth)
        pygame.draw.polygon(surface, (40, 120, 60), smooth, 2)  # outline


def draw_debug(surface: pygame.Surface, blob: BlobBody) -> None:
    """Draw debug overlay: points, springs, pressure normals."""
    # Structural springs
    for s in blob.structural_springs:
        a = (int(s.a.pos.x), int(s.a.pos.y))
        b = (int(s.b.pos.x), int(s.b.pos.y))
        # Color by tension: red=stretched, blue=compressed
        stretch = s.a.pos.distance_to(s.b.pos) - s.rest_length
        r = min(255, max(0, int(128 + stretch * 10)))
        b_color = min(255, max(0, int(128 - stretch * 10)))
        pygame.draw.line(surface, (r, 80, b_color), a, b, 1)

    # Cross springs
    for s in blob.cross_springs:
        a = (int(s.a.pos.x), int(s.a.pos.y))
        b = (int(s.b.pos.x), int(s.b.pos.y))
        pygame.draw.line(surface, (60, 60, 60), a, b, 1)

    # Point masses
    for p in blob.points:
        pygame.draw.circle(surface, (255, 255, 0), (int(p.pos.x), int(p.pos.y)), 3)

    # Centroid
    c = blob.centroid()
    pygame.draw.circle(surface, (255, 0, 0), (int(c.x), int(c.y)), 4)
