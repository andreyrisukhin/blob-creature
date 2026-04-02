from __future__ import annotations
import math


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec2:
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __iadd__(self, other: Vec2) -> Vec2:
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Vec2) -> Vec2:
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: float) -> Vec2:
        self.x *= scalar
        self.y *= scalar
        return self

    def __repr__(self) -> str:
        return f"Vec2({self.x:.3f}, {self.y:.3f})"

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vec2) -> float:
        return self.x * other.y - self.y * other.x

    def length_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.sqrt(self.length_sq())

    def normalized(self) -> Vec2:
        ln = self.length()
        if ln < 1e-12:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / ln, self.y / ln)

    def perpendicular(self) -> Vec2:
        return Vec2(-self.y, self.x)

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def distance_to(self, other: Vec2) -> float:
        return (self - other).length()
