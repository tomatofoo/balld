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
        self._objects = objects
        for obj in objects:
            obj._level = self
    
    @property
    def objects(self: Self) -> set[Object]:
        return self._objects

    @objects.setter
    def objects(self: Self, value: set[Object]) -> None:
        for obj in self._objects:
            obj._level = None
        self._objects = objects
        for obj in objects:
            obj._level = self

