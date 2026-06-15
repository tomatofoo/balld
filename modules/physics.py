import json
from numbers import Real
from typing import Self

import pygame as pg


class Object(object):
    def __init__(self: Self, pos: pg.Vector2) -> None:
        self._level = None
        self._pos = pg.Vector2(pos)

    @property
    def pos(self: Self) -> pg.Vector2:
        return self._pos
    
    @pos.setter
    def pos(self: Self, value: pg.Vector2) -> None:
        self._pos = pg.Vector2(value)

    @classmethod
    def load(cls: type, data: dict) -> None:
        return cls(pg.Vector2(0, 0))


KEY = { # key used when loading level files
    'object': Object,
}


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

    @classmethod
    def load(cls: type, path: str) -> None:
        with open(path, 'r') as file:
            objects = set()
            data = json.load(file)
            for key, value in data['objects']:
                objects.add(KEY[key].load(value))
            return cls(objects)

    def update(self: Self, rel_game_speed: Real) -> None:
        pass

