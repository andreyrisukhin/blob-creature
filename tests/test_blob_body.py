import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from blob_physics import Vec2, BlobBody, BlobWorld


def test_blob_creation():
    blob = BlobBody(center=(100, 100), radius=30, num_points=16)
    assert len(blob.points) == 16
    assert len(blob.structural_springs) == 16
    assert len(blob.cross_springs) == 8


def test_blob_area_near_target():
    blob = BlobBody(center=(400, 300), radius=40, num_points=20)
    import math
    expected = math.pi * 40 * 40
    actual = blob.area()
    # Polygon area of inscribed 20-gon is close to circle
    assert abs(actual - expected) / expected < 0.05


def test_blob_stability_no_gravity():
    """Blob should stay near its center with no gravity."""
    world = BlobWorld(gravity=(0, 0), bounds=None)
    blob = BlobBody(center=(400, 300), radius=40, num_points=20, pressure=60)
    world.add_blob(blob)

    initial_centroid = blob.centroid()
    for _ in range(500):
        world.step(1.0 / 120)

    final_centroid = blob.centroid()
    drift = initial_centroid.distance_to(final_centroid)
    assert drift < 5.0, f"Blob drifted {drift:.1f}px from center"


def test_blob_area_preserved():
    """Area should stay within 10% of target after settling."""
    world = BlobWorld(gravity=(0, 0), bounds=None)
    blob = BlobBody(center=(400, 300), radius=40, num_points=20, pressure=60)
    world.add_blob(blob)

    for _ in range(500):
        world.step(1.0 / 120)

    ratio = blob.area() / blob.target_area
    assert 0.9 < ratio < 1.1, f"Area ratio: {ratio:.3f}"


def test_blob_flattens_under_gravity():
    """Blob should be wider than tall under gravity."""
    world = BlobWorld(gravity=(0, 800), bounds=(800, 600))
    blob = BlobBody(center=(400, 400), radius=40, num_points=20, pressure=40)
    world.add_blob(blob)

    # Let it settle
    for _ in range(3000):
        world.step(1.0 / 120)

    positions = blob.get_positions()
    xs = [p.x for p in positions]
    ys = [p.y for p in positions]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    assert width > height, f"Expected wider than tall: {width:.1f} x {height:.1f}"


def test_blob_round_in_zero_g():
    """Blob should be roughly circular in zero gravity."""
    world = BlobWorld(gravity=(0, 0), bounds=None)
    blob = BlobBody(center=(400, 300), radius=40, num_points=20, pressure=60, surface_tension=1.0)
    world.add_blob(blob)

    for _ in range(1000):
        world.step(1.0 / 120)

    positions = blob.get_positions()
    xs = [p.x for p in positions]
    ys = [p.y for p in positions]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    aspect = width / height if height > 0 else 999
    assert 0.8 < aspect < 1.2, f"Not circular: aspect ratio {aspect:.2f}"
