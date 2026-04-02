from __future__ import annotations
from blob_physics.vec2 import Vec2
from blob_physics.blob_body import BlobBody


class BlobController:
    def __init__(self, move_force: float = 200.0, jump_force: float = 800.0) -> None:
        self.move_force = move_force
        self.jump_force = jump_force

    def apply_intent(self, blob: BlobBody, intent: str, strength: float = 1.0) -> None:
        centroid = blob.centroid()
        n = len(blob.points)

        if intent == "roll_right":
            self._apply_roll(blob, centroid, strength, direction=1.0)
        elif intent == "roll_left":
            self._apply_roll(blob, centroid, strength, direction=-1.0)
        elif intent == "jump":
            self._apply_jump(blob, strength)
        elif intent == "flatten":
            blob.target_area = blob._target_area * (1.0 - 0.3 * strength)
        elif intent == "stretch":
            blob.target_area = blob._target_area * (1.0 + 0.3 * strength)

    def _apply_roll(self, blob: BlobBody, centroid: Vec2, strength: float, direction: float) -> None:
        """Apply tangential forces to bottom points to create rolling motion."""
        # Find bottom-most points (contact region)
        max_y = max(p.pos.y for p in blob.points)
        threshold = max_y - 10.0  # points within 10px of bottom

        for p in blob.points:
            if p.pos.y >= threshold:
                # Apply horizontal force at contact points
                p.add_force(Vec2(self.move_force * strength * direction, 0.0))

    def _apply_jump(self, blob: BlobBody, strength: float) -> None:
        """Apply upward impulse to all points."""
        for p in blob.points:
            p.add_force(Vec2(0.0, -self.jump_force * strength))
