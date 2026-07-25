from __future__ import annotations

import math
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
        self._last_tiles = set()
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
        self._fixed = value

    def _tiles(self: Self, tilesize_inv: Real) -> set[tuple]:
        self._last_tiles = set()
        return self._last_tiles

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

    def _verlet(self: Self,
                prev_pos: pg.Vector2,
                pos: pg.Vector2,
                accel: Real,
                timestep_sq: Real) -> None:
        # will update both prev_pos and pos vectors
        new_prev_pos = pos.copy()
        pos += pos - prev_pos + accel * timestep_sq
        prev_pos.update(new_prev_pos)

    # run one timestep
    def update(self: Self, timestep_sq: Real, objects: set[Object]) -> None:
        if self._fixed:
            self._prev_pos = self._pos.copy()
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
        self._radius = value
        self._diameter = self._radius * 2

    def _tiles(self: Self, tilesize_inv: Real, sets: dict[tuple, set]) -> set[tuple]:
        tiles = set()
        for y in range(
            math.floor((self._pos[1] - self._radius) * tilesize_inv),
            math.floor((self._pos[1] + self._radius) * tilesize_inv) + 1,
        ):
            for x in range(
                math.floor((self._pos[0] - self._radius) * tilesize_inv),
                math.floor((self._pos[0] + self._radius) * tilesize_inv) + 1,
            ):
                tiles.add((x, y))
        self._last_tiles = tiles
        return tiles

    def update(self: Self, timestep_sq: Real, objects: set[Object]) -> None:
        super().update(timestep_sq, objects)
        for obj in objects:
            if obj is self:
                continue
            if isinstance(obj, Circle):
                cur_dist = self._pos.distance_to(obj._pos)
                new_dist = self._radius + obj._radius
                if cur_dist < new_dist:
                    dist = new_dist - cur_dist
                    # I don't know any other way to condense this
                    if self._fixed:
                        obj._collide(self._pos, dist)
                    elif obj._fixed:
                        self._collide(obj._pos, dist)
                    else:
                        dist *= 0.5
                        obj._collide(self._pos, dist)
                    self._collide(obj._pos, dist)
        # TEMP
        if self._pos[1] > 270 - self._radius:
            self._pos[1] = 270 - self._radius
        if self._pos[1] < self._radius:
            self._pos[1] = self._radius
        if self._pos[0] > 360 - self._radius:
            self._pos[0] = 360 - self._radius
        if self._pos[0] < self._radius:
            self._pos[0] = self._radius

    def render(self: Self, surf: pg.Surface, t: Real=1) -> None:
        pg.draw.circle(surf, (255, 255, 255), self._pos, self._radius)


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
    
    def update(self: Self, timestep_sq: Real, objects: set[Object]) -> None:
        pass


KEY = { # key used when loading level files
    'object': Object,
    'gon': Gon,
}


class Level(object):
    def __init__(self: Self,
                 objects: set[Object],
                 tilesize: Real=16,
                 timestep: Real=0.01) -> None:
        # https://www.gafferongames.com/post/fix_your_timestep
        self._objects = objects
        for obj in objects:
            obj._level = self
        self.tilesize = tilesize
        self._update_sets()
        self.timestep = timestep
        self._accumulator = 0

    @property
    def objects(self: Self) -> set[Object]:
        return self._objects

    @objects.setter
    def objects(self: Self, value: set[Object]) -> None:
        for obj in self._objects:
            obj._level = None
        self._objects = value
        for obj in value:
            obj._level = self
    
    @property
    def tilesize(self: Self) -> Real:
        return self._tilesize

    @tilesize.setter
    def tilesize(self: Self, value: Real) -> None:
        self._tilesize = value
        self._tilesize_inv = 1 / value

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
    
    def _update_sets(self: Self) -> None:
        self._sets = {}
        for obj in self._objects:
            for tile in obj._tiles(self._tilesize_inv, self._sets):
                objects = self._sets.get(tile)
                if objects is None:
                    self._sets[tile] = {obj}
                else:
                    objects.add(obj)

    def update(self: Self, rel_game_speed: Real) -> None:
        self._accumulator += rel_game_speed
        while self._accumulator >= self._timestep:
            self._update_sets()
            for obj in self._objects:
                objects = set()
                for tile in obj._last_tiles:
                    objects |= self._sets[tile]
                obj.update(self._timestep_sq, objects)
            self._accumulator -= self._timestep

    def render(self: Self, surf: pg.Surface) -> None:
        for obj in self._objects:
            obj.render(surf, self._accumulator / self._timestep)

