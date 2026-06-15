from numbers import Real
from typing import Self

import pygame as pg


class Object(object):
    def __init__(self: Self) -> None:
        self._level = None


class Level(object):
    def __init__(self: Self, objects: set[Object]) -> None:
        pass

