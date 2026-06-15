from numbers import Real
from typing import Self

import pygame as pg


class Object(object):
    def __init__(self: Self, pos: pg.Vector2) -> None:
        self._level = None
        self._pos = pos

    @property
    def pos(self: Self) -> pg.Vector2:
        return self._pos
    
    @pos.setter
    def pos(self: Self, value: pg.Vector2) -> None:
        self._pos = value


class Level(object):
    def __init__(self: Self, objects: set[Object]) -> None:
        pass

