import json
from numbers import Real
from typing import Self

import pygame as pg


class Object(object):
    def __init__(self: Self,
                 pos: pg.Vector2,
                 mass: Real=1,
                 force: pg.Vector2=(0, 0)) -> None:
        self._level = None
        self._pos = pg.Vector2(pos)
        self._prev_pos = pg.Vector2(pos)
        self._mass = mass
        self._force = pg.Vector2(force)

    @property
    def pos(self: Self) -> pg.Vector2:
        return self._pos
    
    @pos.setter
    def pos(self: Self, value: pg.Vector2) -> None:
        self._pos = pg.Vector2(value)

    @property
    def prev_pos(self: Self) -> pg.Vector2:
        return self._prev_pos

    @property
    def mass(self: Self) -> Real:
        return self._mass

    @mass.setter
    def mass(self: Self, value: Real) -> None:
        self._mass = value

    @property
    def force(self: Self) -> pg.Vector2:
        return self._force

    @force.setter
    def force(self: Self, value: pg.Vector2) -> None:
        self._force = value

    @classmethod
    def load(cls: type, data: dict) -> None:
        return cls(pg.Vector2(0, 0))

    def _verlet(self: Self,
                prev_pos: pg.Vector2,
                pos: pg.Vector2,
                accel: Real,
                timestep_sq: Real) -> None:
        # will update both prev_pos and pos vectors
        new_prev_pos = pos.copy()
        pos += pos * (1 + accel * timestep_sq) - prev_pos
        prev_pos.update(new_prev_pos)

    # will only do own part of collision; the other object handles its part
    def collide(self: Self,
                new_dist: Real,
                pos: pg.Vector2,
                cur_dist: Real) -> None:
        self._pos.move_towards_ip(pos, (cur_dist - new_dist) / 2)
    
    # run jakobsen constraint
    def constrain(self: Self) -> None:
        pass
    
    # run one timestep
    def update(self: Self, timestep_sq: Real) -> None:
        self._verlet(
            self._prev_pos,
            self._pos,
            self._force / self._mass,
            timestep_sq,
        )

    # t is interpolant for interpolated rendering
    def render(self: Self, surf: pg.Surface, t: Real=1) -> None:
        pass


class Gon(Object):
    def __init__(self: Self) -> None:
        pass

    def collide(self: Self, obj: Object) -> None:
        pass
    
    def update(self: Self) -> None:
        pass


KEY = { # key used when loading level files
    'object': Object,
    'gon': Gon,
}


class Level(object):
    def __init__(self: Self,
                 objects: set[Object],
                 timestep: Real=0.01) -> None:
        self._objects = objects
        for obj in objects:
            obj._level = self
        # https://www.gafferongames.com/post/fix_your_timestep/
        self.timestep = timestep
        self._accumulator = 0

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

    @property
    def timestep(self: Self) -> Real:
        return self._timestep

    @timestep.setter
    def timestep(self: Self, value: Real) -> None:
        self._timestep = value
        self._timestep_sq = self._timestep * self._timestep

    @classmethod
    def load(cls: type, path: str) -> None:
        with open(path, 'r') as file:
            objects = set()
            data = json.load(file)
            for key, value in data['objects']:
                objects.add(KEY[key].load(value))
            return cls(objects)

    def update(self: Self, rel_game_speed: Real) -> None:
        self._accumulator += rel_game_speed
        while self._accumulator >= self._timestep:
            for obj in self._objects:
                obj.update(self._timestep_sq)
            self._accumulator -= self._timestep

    def render(self: Self) -> None:
        for obj in self._objects:
            obj.render(self._accumulator / self._timestep)

