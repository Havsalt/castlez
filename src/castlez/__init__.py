import random
import math

import keyboard
import colex
from charz import (
    Engine,
    TransformComponent,
    Screen,
    Node2D,
    Sprite,
    Label,
    Camera,
    ColorValue,
    Vec2,
    lerp,
)

from .text_collider import TextCollider

# cool colors:
# '\x1b[38;2;78;214;77m\x1b[48;2;18;111;254m'    or '\x1b[38;2;78;214;77m\x1b[48;2;18;111;254m'
# '\x1b[38;2;188;121;0m\x1b[48;2;174;163;97m'    or '\x1b[38;2;188;121;0m\x1b[48;2;174;163;97m'
# '\x1b[38;2;52;54;28m\x1b[48;2;233;1;103m'      or '\x1b[38;2;52;54;28m\x1b[48;2;233;1;103m'
# '\x1b[38;2;106;39;162m\x1b[48;2;58;84;185m'    or '\x1b[38;2;106;39;162m\x1b[48;2;58;84;185m'
# '\x1b[38;2;123;112;133m\x1b[48;2;72;101;116m'  or '\x1b[38;2;123;112;133m\x1b[48;2;72;101;116m'
# '\x1b[38;2;180;227;185m\x1b[48;2;168;101;234m' or '\x1b[38;2;180;227;185m\x1b[48;2;168;101;234m'
# '\x1b[38;2;101;153;99m\x1b[48;2;132;128;206m'
# '\x1b[38;2;86;45;99m\x1b[48;2;140;56;175m'
# '\x1b[38;2;203;84;193m\x1b[48;2;207;179;198m'


class SmoothCamera(Camera):
    # _PERCENT_PER_SECOND: float = 2.90
    top_level = True

    def update(self) -> None:
        assert isinstance(self.parent, TransformComponent)
        self.global_position = self.global_position.lerp(
            self.parent.global_position,
            # self._PERCENT_PER_SECOND * delta,
            0.50,
        )
        if self.global_position.distance_to(self.parent.global_position) < 0.25:
            self.global_position = self.parent.global_position


class Marker(Sprite):
    z_index = -2
    centered = True
    texture = ["[?]"]


class Knight(TextCollider, Sprite):
    z_index = -1
    color = colex.KHAKI
    texture = ["@"]

    def __init__(self) -> None:
        self._marker = Marker()

    def update(self) -> None:
        velocity = Vec2.ZERO
        if keyboard.is_pressed("d"):
            velocity.x += 1
        if keyboard.is_pressed("a"):
            velocity.x -= 1
        if keyboard.is_pressed("w"):
            velocity.y -= 1
        if keyboard.is_pressed("s"):
            velocity.y += 1
        self.move_and_slide(velocity)
        if keyboard.is_pressed("space"):
            self._marker.global_position = self.global_position


class Tower(TextCollider, Sprite):
    texture = [
        "#.#.#",
        "#####",
        "#####",
        "#####",
    ]


class Gate(TextCollider, Sprite):
    transparency = " "
    texture = [
        " #.#.#.#.# ",
        "|#########|",
        "|###| |###|",
    ]


class Castle(Node2D):
    def __init__(
        self,
        *watch_for: Knight,
        position: Vec2,
        color: ColorValue = colex.NONE,
        z_index: int | None = None,
    ) -> None:
        super().__init__(position=position)
        self.tower_left = Tower(
            self,
            position=Vec2(-10, -4),
            color=color,
            z_index=z_index,
        )
        self.gate = Gate(
            self,
            position=Vec2(-5, -3),
            color=color,
            z_index=z_index,
        )
        self.tower_right = Tower(
            self,
            position=Vec2(6, -4),
            color=color,
            z_index=z_index,
        )
        self._watch_for: list[Knight] = list(watch_for)
        self._entries: list[MagicGate] = []

    def update(self) -> None:
        for node in self._watch_for:
            if node.global_position - self.global_position == Vec2.ZERO:
                entry = random.choice(self._entries)
                node.global_position = entry.global_position + Vec2(0, 2)


class MagicGate(Sprite):
    _COLORS: list[ColorValue] = [
        colex.BLUE_VIOLET,
        colex.BLUE_VIOLET,
        colex.AQUAMARINE,
        colex.AZURE,
        colex.FUCHSIA,
    ]
    transparency = " "
    texture = [
        [*"\\"],
        [*" |"],
        [*"  )"],
        [*" |"],
        [*"/"],
    ]
    color = _COLORS[0]

    def __init__(self) -> None:
        self._watch_for: list[Knight] = []
        self._exits: list[Node2D] = []
        self.color = random.choice(self._COLORS)

    def update(self) -> None:
        self.color = random.choice(self._COLORS)
        for node in self._watch_for:
            if node.global_position - self.global_position == Vec2(1, 2):
                chosen_exit = random.choice(self._exits)
                location = chosen_exit.global_position + Vec2(0, 1)
                node.global_position = location


class Spinner(Sprite):
    centered = True
    texture = [
        "#",
        "##",
        "###",
        "##",
        "#",
    ]

    def look_at(self, location: Vec2) -> None:
        self.global_rotation = -self.global_position.angle_to(location)


class Game(Engine):
    clear_console = True
    screen = Screen(auto_resize=True)

    def __init__(self) -> None:
        self.knight = Knight()
        self.castle1 = Castle(
            self.knight,
            position=Vec2(5, -3),
            z_index=1,
            color=colex.LIGHT_CYAN,
        )
        self.castle2 = Castle(
            self.knight,
            position=Vec2(20, 9),
            z_index=1,
            color=colex.CRIMSON,
        )
        self.castle3 = Castle(
            self.knight,
            position=Vec2(-24, 10),
            z_index=1,
            color=colex.SLATE_BLUE,
        )
        # self.castle3.tower_right2 = Tower(
        #     self.castle3,
        #     position=Vec2(12, -3),
        #     color=self.castle3.tower_right.color,
        # )  # type: ignore
        # self.castle3.tower_right3 = Tower(
        #     self.castle3,
        #     x=18,
        #     y=-1,
        #     color=self.castle3.color,
        # )
        self.decoration = Sprite(
            self.castle1,
            position=Vec2(-1, -3),
            texture=["|||"],
            color=self.castle1.tower_right.color,
            z_index=2,
        )
        self.magic_gate = MagicGate().with_position(x=-400).with_z_index(-2)
        self.magic_gate._watch_for.append(self.knight)
        castles = [self.castle1, self.castle2, self.castle3]
        self.magic_gate._exits.extend(castles)
        for castle in castles:
            castle._entries.append(self.magic_gate)
        self.spinner1 = Spinner(
            self.magic_gate,
            position=Vec2(-20, 7),
            color=colex.from_random(),
        )
        self.spinner2 = Spinner(
            self.magic_gate,
            position=Vec2(-20, -3),
            color=colex.from_random(),
        )
        # Set current camera to be smooth and centered
        Camera.current = SmoothCamera(
            self.knight,
            mode=Camera.MODE_CENTERED | Camera.MODE_INCLUDE_SIZE,
        )
        # Dev
        self.rand_label = Label(
            self.knight,
            text="#????",
            position=Vec2(0, 2),
            centered=True,
            z_index=-5,
        )

    def update(self) -> None:
        hex_value = "".join("0123456789ABCDEF"[random.randint(0, 15)] for _ in range(6))
        self.rand_label.text = "#" + hex_value
        self.rand_label.color = colex.from_hex(hex_value)

        self.spinner1.look_at(self.knight.global_position)
        self.spinner2.look_at(self.knight.global_position)


def main() -> None:
    game = Game()
    game.run()
