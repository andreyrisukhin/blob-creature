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


def _draw_arrow(surface: pygame.Surface, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
    """Draw a line with a small arrowhead."""
    pygame.draw.line(surface, color, start, end, 2)
    # Arrowhead
    dx, dy = end[0] - start[0], end[1] - start[1]
    ln = math.sqrt(dx * dx + dy * dy)
    if ln < 4:
        return
    dx, dy = dx / ln, dy / ln
    size = 5
    ax = end[0] - dx * size - dy * size * 0.5
    ay = end[1] - dy * size + dx * size * 0.5
    bx = end[0] - dx * size + dy * size * 0.5
    by = end[1] - dy * size - dx * size * 0.5
    pygame.draw.polygon(surface, color, [end, (int(ax), int(ay)), (int(bx), int(by))])


def draw_debug(surface: pygame.Surface, blob: BlobBody, gravity: Vec2 | None = None) -> None:
    """Draw debug overlay: points, springs, force vectors, velocity."""
    FORCE_SCALE = 0.3  # pixels per unit force
    VEL_SCALE = 3.0    # pixels per unit velocity

    # Structural springs (color by tension)
    for s in blob.structural_springs:
        a = (int(s.a.pos.x), int(s.a.pos.y))
        b = (int(s.b.pos.x), int(s.b.pos.y))
        stretch = s.a.pos.distance_to(s.b.pos) - s.rest_length
        r = min(255, max(0, int(128 + stretch * 10)))
        b_color = min(255, max(0, int(128 - stretch * 10)))
        pygame.draw.line(surface, (r, 80, b_color), a, b, 1)

    # Cross springs
    for s in blob.cross_springs:
        a = (int(s.a.pos.x), int(s.a.pos.y))
        b = (int(s.b.pos.x), int(s.b.pos.y))
        pygame.draw.line(surface, (60, 60, 60), a, b, 1)

    # Per-point: force vectors and velocity vectors
    for p in blob.points:
        px, py = int(p.pos.x), int(p.pos.y)

        # Net force (cyan)
        fx = px + int(p.force.x * FORCE_SCALE)
        fy = py + int(p.force.y * FORCE_SCALE)
        if abs(fx - px) > 1 or abs(fy - py) > 1:
            _draw_arrow(surface, (px, py), (fx, fy), (0, 200, 255))

        # Velocity (yellow)
        vel = p.velocity
        vx = px + int(vel.x * VEL_SCALE)
        vy = py + int(vel.y * VEL_SCALE)
        if abs(vx - px) > 1 or abs(vy - py) > 1:
            _draw_arrow(surface, (px, py), (vx, vy), (255, 255, 0))

    # Point masses (white dots on top)
    for p in blob.points:
        pygame.draw.circle(surface, (255, 255, 255), (int(p.pos.x), int(p.pos.y)), 2)

    # Centroid
    c = blob.centroid()
    cx, cy = int(c.x), int(c.y)
    pygame.draw.circle(surface, (255, 0, 0), (cx, cy), 4)

    # Gravity vector at centroid (magenta)
    if gravity is not None:
        gx = cx + int(gravity.x * FORCE_SCALE * 2)
        gy = cy + int(gravity.y * FORCE_SCALE * 2)
        _draw_arrow(surface, (cx, cy), (gx, gy), (255, 0, 255))

    # Net velocity of centroid (green)
    avg_vel = Vec2(0, 0)
    for p in blob.points:
        avg_vel += p.velocity
    avg_vel = avg_vel * (1.0 / len(blob.points))
    mvx = cx + int(avg_vel.x * VEL_SCALE * 5)
    mvy = cy + int(avg_vel.y * VEL_SCALE * 5)
    if abs(mvx - cx) > 2 or abs(mvy - cy) > 2:
        _draw_arrow(surface, (cx, cy), (mvx, mvy), (0, 255, 100))
