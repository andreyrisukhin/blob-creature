from __future__ import annotations
from blob_physics.vec2 import Vec2
from blob_physics.point_mass import PointMass


def point_vs_segment(
    point: PointMass,
    seg_a: Vec2,
    seg_b: Vec2,
    friction: float = 0.3,
) -> bool:
    """Push point out of a line segment if penetrating. Returns True if collision occurred."""
    edge = seg_b - seg_a
    edge_len = edge.length()
    if edge_len < 1e-12:
        return False

    edge_dir = edge * (1.0 / edge_len)
    to_point = point.pos - seg_a

    # Project point onto segment
    t = to_point.dot(edge_dir)
    if t < 0.0 or t > edge_len:
        return False

    # Normal pointing "upward" (away from solid side) in screen coords
    # For a left-to-right segment, this points toward negative y (visually up)
    normal = Vec2(edge_dir.y, -edge_dir.x)
    dist = to_point.dot(normal)

    if dist < 0.0:
        # Point has crossed to the solid side — push it back out
        point.pos += normal * (-dist)
        point.old_pos += normal * (-dist)

        # Apply friction: reduce tangential velocity
        vel = point.pos - point.old_pos
        tangential_vel = edge_dir * vel.dot(edge_dir)
        point.old_pos += tangential_vel * friction
        return True

    return False


def point_vs_bounds(
    point: PointMass,
    width: float,
    height: float,
    friction: float = 0.3,
) -> None:
    """Keep point within rectangular bounds."""
    if point.pos.y > height:
        point.pos.y = height
        point.old_pos.y = height
        vel = point.pos - point.old_pos
        point.old_pos.x += vel.x * friction
    if point.pos.y < 0:
        point.pos.y = 0
        point.old_pos.y = 0
    if point.pos.x < 0:
        point.pos.x = 0
        point.old_pos.x = 0
    if point.pos.x > width:
        point.pos.x = width
        point.old_pos.x = width
