from __future__ import annotations
from blob_physics.vec2 import Vec2
from blob_physics.blob_body import BlobBody


class BlobController:
    def __init__(
        self,
        move_force: float = 600.0,
        jump_squash: float = 0.45,
        jump_expand: float = 1.8,
        squash_frames: int = 4,
    ) -> None:
        self.move_force = move_force

        # Jump state machine
        self.jump_squash = jump_squash      # area multiplier during wind-up
        self.jump_expand = jump_expand      # area multiplier during launch
        self.squash_frames = squash_frames  # how long to squash before release
        self._jump_timer: int = -1          # -1 = idle, 0..squash_frames = squashing, then launch
        self._base_area: float = 0.0

        # Stick landing state
        self._sticking: bool = False

    def apply_intent(self, blob: BlobBody, intent: str, strength: float = 1.0) -> None:
        if intent == "roll_right":
            self._apply_move(blob, strength, direction=1.0)
        elif intent == "roll_left":
            self._apply_move(blob, strength, direction=-1.0)
        elif intent == "jump":
            self._start_jump(blob)
        elif intent == "stick":
            self._stick_landing(blob)
        elif intent == "unstick":
            self._sticking = False

    def update(self, blob: BlobBody) -> None:
        """Call once per frame to advance jump state machine."""
        if self._jump_timer >= 0:
            self._jump_timer += 1
            if self._jump_timer <= self.squash_frames:
                # Squash phase: compress the blob
                blob.target_area = self._base_area * self.jump_squash
            else:
                # Launch phase: expand rapidly, then restore
                blob.target_area = self._base_area * self.jump_expand
                # After one frame of expansion, restore and end
                if self._jump_timer > self.squash_frames + 1:
                    blob.target_area = self._base_area
                    self._jump_timer = -1

        if self._sticking:
            self._apply_stick(blob)

    def _apply_move(self, blob: BlobBody, strength: float, direction: float) -> None:
        force = Vec2(self.move_force * strength * direction, 0.0)
        for p in blob.points:
            p.add_force(force)

    def _start_jump(self, blob: BlobBody) -> None:
        if self._jump_timer >= 0:
            return  # already jumping
        self._base_area = blob._target_area
        self._jump_timer = 0

    def _stick_landing(self, blob: BlobBody) -> None:
        """Kill vertical velocity on contact points to cancel bounce."""
        self._sticking = True

    def _apply_stick(self, blob: BlobBody) -> None:
        """Dampen vertical velocity on bottom points each frame."""
        max_y = max(p.pos.y for p in blob.points)
        threshold = max_y - 8.0
        for p in blob.points:
            if p.pos.y >= threshold:
                # Kill vertical velocity by snapping old_pos.y to pos.y
                p.old_pos.y = p.pos.y
