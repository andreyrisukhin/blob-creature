from __future__ import annotations
from blob_physics.vec2 import Vec2
from blob_physics.blob_body import BlobBody


class BlobController:
    def __init__(self, move_force: float = 150.0, jump_impulse: float = 5.0) -> None:
        self.move_force = move_force
        self.jump_impulse = jump_impulse

    def apply_intent(self, blob: BlobBody, intent: str, strength: float = 1.0) -> None:
        if intent == "roll_right":
            self._apply_move(blob, strength, direction=1.0)
        elif intent == "roll_left":
            self._apply_move(blob, strength, direction=-1.0)
        elif intent == "jump":
            self._apply_jump(blob, strength)
        elif intent == "flatten":
            blob.target_area = blob._target_area * (1.0 - 0.3 * strength)
        elif intent == "stretch":
            blob.target_area = blob._target_area * (1.0 + 0.3 * strength)

    def _apply_move(self, blob: BlobBody, strength: float, direction: float) -> None:
        """Apply horizontal force to all points — smoother than bottom-only."""
        force = Vec2(self.move_force * strength * direction, 0.0)
        for p in blob.points:
            p.add_force(force)

    def _apply_jump(self, blob: BlobBody, strength: float) -> None:
        """Apply upward velocity impulse (directly modify old_pos for Verlet)."""
        impulse = Vec2(0.0, -self.jump_impulse * strength)
        for p in blob.points:
            p.old_pos -= impulse
