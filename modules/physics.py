from __future__ import annotations

import json
from numbers import Real
from typing import Self

import pygame as pg


class Object(object):
    def __init__(self: Self,
                 pos: pg.Vector2,
                 mass: Real=1,
                 force: pg.Vector2=(0, 0),
                 fixed: bool=0) -> None:
        self._level = None
        self._pos = pg.Vector2(pos)
        self._prev_pos = pg.Vector2(pos)
        self._mass = mass
        self._force = pg.Vector2(force)
        self._fixed = fixed

    @classmethod
    def load(cls: type, data: dict) -> Self:
        return cls(**data)

    @property
    def bound(self: Self) -> pg.FRect:
        return pg.FRect(self._pos[0], self._pos[1], 0, 0)

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

    @property
    def fixed(self: Self) -> bool:
        return self._fixed

    @fixed.setter
    def fixed(self: Self, value: bool) -> None:
        self._bool = value

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
    # each successive object type that is defined must implement collisions 
    # with all other objectssikx 
    def _collide(self: Self, pos: pg.Vector2, dist: Real) -> None:
        if self._fixed:
            return None
        self._pos.move_towards_ip(pos, -dist)
    
    # run jakobsen constraint
    def _constrain(self: Self) -> None:
        pass
    
    # run one timestep
    def update(self: Self, timestep_sq: Real, objects: set[Object]) -> None:
        if self._fixed:
            return None
        self._verlet(
            self._prev_pos,
            self._pos,
            self._force / self._mass,
            timestep_sq,
        )

    # t is interpolant for interpolated rendering
    def render(self: Self, surf: pg.Surface, t: Real=1) -> None:
        pass


class Circle(Object):
    def __init__(self: Self,
                 pos: pg.Vector2,
                 radius: Real,
                 mass: Real=1,
                 force: pg.Vector2=(0, 0),
                 fixed: bool=0) -> None:
        super().__init__(pos, mass, force, fixed)
        self.radius = radius

    @property
    def bound(self: Self) -> pg.FRect:
        return pg.FRect(
            self._pos[0] - self._radius,
            self._pos[1] - self._radius,
            self._diameter,
            self._diameter,
        )

    @property
    def radius(self: Self) -> Real:
        return self._radius

    @radius.setter
    def radius(self: Self, value: Real) -> None:
        self._radius = valuehttps://turbowarp.org/1307198399?fps=60
        self._diameter = self._radius * 2

    def update(self: Self, timestep_sq: Real, objects: Object) -> None:
        super().update(timestep_sq)
        for obj in self._level._objects:
            if obj is self:
                continue
            if isinstance(obj, Circle):
                cur_dist = self._pos.distance_to(obj)
                new_dist = self._radius + obj._radius
                if cur_dist < new_dist:
                    dist = new_dist - cur_dist
                    if self._fixed:
                        obj._collide(self._pos, dist)
                    else:
                        dist *= 0.5
                        obj._collide(self._pos, dist)
                        self._collide(obj._pos, dist)


class Gon(Object):
    def __init__(self: Self,
                 vertices: tuple[Circle],
                 connections: tuple[tuple[int, int]],
                 force: pg.Vector2=(0, 0)) -> None:
        mass = 0
        for vertex in vertices:
            mass += vertex._mass
        super().__init__(vertices[0][0], mass, force)
        self.vertices = vertices
        self._connections = connections

    @classmethod
    def load(self: Self, data: dict) -> None:
        pass

    @property
    def mass(self: Self) -> Real:
        return self._mass
        
    @property
    def vertices(self: Self) -> tuple[pg.Vector2]:
        return self._vertices

    @vertices.setter
    def vertices(self: Self, value: tuple[pg.Vector2]) -> None:
        self._vertices = value

    @property
    def connections(self: Self) -> tuple[tuple[int, int]]:
        return self._connections

    @connections.setter
    def connections(self: Self, value: tuple[tuple[int, int]]) -> None:
        self._connections = value

    def _collide(self: Self, obj: Object) -> None:
        pass
    
    def update(self: Self, timestep_sq: Real) -> None:
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

