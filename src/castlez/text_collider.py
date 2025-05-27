from __future__ import annotations

from typing import Any

from charz import Scene, TransformComponent, TextureComponent, Self, group
from linflex import Vec2


TEXT_COLLIDER_GID = "text_collider"


@group(TEXT_COLLIDER_GID)
class TextCollider:  # Component (mixin class)
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        return super().__new__(cls, *args, **kwargs)

    def _get_texture_global_position(self) -> Vec2:
        assert isinstance(self, TransformComponent)
        return self.global_position

    def move_and_collide(self, distance: Vec2) -> None:
        assert isinstance(self, TextureComponent)
        old_position = self.position.copy()
        self.position += distance
        if collider := self.get_collider():
            self.position = old_position
            self.position.y = (
                collider._get_texture_global_position().y - self.get_texture_size().y
            )

    def move_and_slide(self, distance: Vec2) -> None:
        assert isinstance(self, TextureComponent)
        old_position = self.position.copy()
        self.position.x += distance.x
        signs = distance.sign()
        if collider := self.get_collider():
            assert isinstance(collider, TextureComponent)
            self.position = old_position
            if signs.x == 1:
                self.position.x = (
                    collider._get_texture_global_position().x
                    - self.get_texture_size().x
                )
            elif signs.x == -1:
                self.position.x = (
                    collider._get_texture_global_position().x
                    + collider.get_texture_size().x
                )
        old_position = self.position.copy()
        self.position.y += distance.y
        if collider := self.get_collider():
            assert isinstance(collider, TextureComponent)
            self.position = old_position
            if signs.y == 1:
                self.position.y = (
                    collider._get_texture_global_position().y
                    - self.get_texture_size().y
                )
            elif signs.y == -1:
                self.position.y = (
                    collider._get_texture_global_position().y
                    + collider.get_texture_size().y
                )

    def is_on_floor(self) -> bool:
        old_position = self.position.copy()
        self.position.y += 1
        on_floor = self.is_colliding()
        self.position = old_position
        return on_floor

    def is_colliding(self) -> bool:
        for collider in Scene.current.get_group_members(TEXT_COLLIDER_GID):
            assert isinstance(collider, TextCollider)
            if collider is self:
                continue
            elif self.is_colliding_with(collider):
                return True
        return False

    def get_collider(self) -> TextCollider | None:
        for collider in Scene.current.get_group_members(TEXT_COLLIDER_GID):
            assert isinstance(collider, TextCollider)
            if collider is self:
                continue
            elif self.is_colliding_with(collider):
                return collider
        return None

    def is_colliding_with(self, other: TextCollider) -> bool:
        assert isinstance(self, TextureComponent)
        assert isinstance(other, TextureComponent)
        # basic implementation
        position = self._get_texture_global_position()
        start = other._get_texture_global_position()
        texture_size = self.get_texture_size()  # cache using variable
        rect = (start, start + other.get_texture_size())  # start, end
        return any(  # any intersects
            self._point_intersects_with(point, rect)
            for point in [
                position + Vec2(0, 1),
                position + texture_size,
                position + Vec2(texture_size.x, 1),
                position + Vec2(0, texture_size.y),
            ]
        )

    def _point_intersects_with(self, point: Vec2, rect: tuple[Vec2, Vec2]) -> bool:
        start, end = rect
        x_inside = start.x < point.x < end.x
        y_inside = start.y < point.y <= end.y
        return x_inside and y_inside
