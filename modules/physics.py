from __future__ import annotations

import math
import json
from numbers import Real
from typing import Self
from typing import Optional

import pygame as pg
from pygame.typing import Point


class Object(object):
    def __init__(self: Self,
                 pos: pg.Vector2,
                 mass: Real=1,
                 force: pg.Vector2=(0, 0),
                 fixed: bool=0,
                 whitelist: Optional[set[type]]=set(),
                 texture: Optional[pg.Surface]=None) -> None:
        self._level = None
        self._last_tiles = set()
        self._pos = pg.Vector2(pos)
        self._prev_pos = pg.Vector2(pos)
        self._mass = mass
        self._mass_inv = 1 / mass
        self._force = pg.Vector2(force)
        self._fixed = fixed
        if whitelist is None: # whitelist won't include base class
            whitelist = set()
        self._whitelist = whitelist
        self.texture = texture # so texture is handeld by child classes

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
        self._mass_inv = 1 / value

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

    @property
    def whitelist(self: Self) -> set[Object]:
        return self._whitelist

    @whitelist.setter
    def whitelist(self: Self, value: set[Object]) -> None:
        self._whitelist = value

    @property
    def texture(self: Self) -> Optional[pg.Surface]:
        return self._texture

    @texture.setter
    def texture(self: Self, value: Optional[pg.Surface]) -> None:
        self._texture = value

    def _tiles(self: Self, tilesize_inv: Real) -> set[tuple]:
        self._last_tiles = set()
        return self._last_tiles

    def _verlet(self: Self,
                prev_pos: pg.Vector2,
                pos: pg.Vector2,
                accel: Real,
                timestep_sq: Real) -> None:
        # will update both prev_pos and pos vectors
        new_prev_pos = pos.copy()
        pos += pos - prev_pos + accel * timestep_sq
        prev_pos.update(new_prev_pos)

    # solve constraints
    def _constrain(self: Self, objects: set[Object]) -> None:
        pass

    # run one timestep
    def update(self: Self,
               timestep_sq: Real,
               objects: set[Object]=set(),
               force: pg.Vector2=(0, 0)) -> None:
        if self._fixed:
            self._prev_pos = self._pos.copy()
        else:
            self._verlet(
                self._prev_pos,
                self._pos,
                (self._force + force) / self._mass,
                timestep_sq,
            )
        self._constrain(objects)

    # t is interpolant for interpolated rendering
    def render(self: Self, surf: pg.Surface, t: Real=1) -> None:
        if self._texture is not None:
            surf.blit(self._texture, self._pos)


class Circle(Object):
    def __init__(self: Self,
                 pos: pg.Vector2,
                 radius: Real,
                 mass: Real=1,
                 force: pg.Vector2=(0, 0),
                 fixed: bool=0,
                 whitelist: Optional[set[type]]=None,
                 texture: Optional[pg.Surface]=None) -> None:
        if whitelist is None:
            whitelist = {Circle}
        super().__init__(pos, mass, force, fixed, whitelist, texture)
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

    @property
    def texture(self: Self) -> Optional[pg.Surface]:
        return self._texture

    @texture.setter
    def texture(self: Self, value: Optional[pg.Surface]) -> None:
        self._texture = value
        if value is not None:
            self._texture_offset = (
                self._texture.width * 0.5,
                self._texture.height * 0.5,
            )

    def _tiles(self: Self, tilesize_inv: Real) -> set[tuple]:
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

    def _constrain(self: Self, objects: set[Object]) -> None:
        for obj in objects:
            if obj is self:
                continue
            if Circle in self._whitelist and isinstance(obj, Circle):
                diff = obj._pos - self._pos
                cur_dist = diff.magnitude()
                new_dist = self._radius + obj._radius
                if 0 < cur_dist < new_dist:
                    dist = new_dist - cur_dist
                    if not (self._fixed or obj._fixed):
                        dist *= 0.5
                    rel = diff / cur_dist * dist
                    avg = 0
                    count = 0
                    if not obj._fixed:
                        avg += obj._mass_inv
                        count += 1
                    if not self._fixed:
                        avg += self._mass_inv
                        count += 1
                    if count:
                        avg /= count
                    if not obj._fixed:
                        obj._pos += rel * obj._mass_inv / avg
                    if not self._fixed:
                        self._pos -= rel * self._mass_inv / avg
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
        pos = self._prev_pos.lerp(self._pos, t)
        if self._texture is None:
            pg.draw.circle(
                surf,
                (255, 255, 255),
                pos,
                self._radius,
            )
        else:
            surf.blit(self._texture, self._pos - self._texture_offset)


class Gon(Object):
    def __init__(self: Self,
                 vertices: tuple[Circle],
                 connections: tuple[tuple[int, int, bool]],
                 stiffness: int=1,
                 average: bool=0,
                 force: pg.Vector2=(0, 0),
                 whitelist: Optional[set[type]]={Circle},
                 texture: Optional[pg.Surface]=None,
                 texture_pivot: Optional[tuple[Point, int, int]]=None) -> None:
        mass = 0
        for vertex in vertices:
            mass += vertex._mass
        if whitelist is None:
            whitelist = {Circle, Gon}
        super().__init__(
            vertices[0]._pos,
            mass,
            force,
            whitelist=whitelist,
            texture=texture,
        )
        self._vertices = vertices
        self.connections = connections
        self._stiffness = stiffness
        self._average = average
        self.texture_pivot = texture_pivot

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
        self._dists = []
        for connection in value:
            self._dists.append(self._vertices[connection[0]]._pos.distance_to(
                self._vertices[connection[1]]._pos
            ))

    @property
    def stiffness(self: Self) -> int:
        return self._stiffness

    @stiffness.setter
    def stiffness(self: Self, value: int) -> None:
        self._stiffness = value

    @property
    def stiffness(self: Self) -> bool:
        return self._average

    @stiffness.setter
    def stiffness(self: Self, value: bool) -> None:
        self._average = value

    @property
    def texture(self: Self) -> Optional[pg.Surface]:
        return self._texture

    @texture.setter
    def texture(self: Self, value: Optional[pg.Surface]) -> None:
        self._texture = value

    @property
    def texture_pivot(self: Self) -> tuple[int, int]:
        return self._texture_pivot

    @texture_pivot.setter
    def texture_pivot(self: Self, value: tuple[Point, int, int]) -> None:
        self._texture_pivot = value
        if self._texture is not None and value is not None and value[2] != -1:
            diff = (
                self._vertices[value[2]]._pos - self._vertices[value[1]]._pos
            )
            self._texture_base_magnitude = diff.magnitude()
            if self._texture_base_magnitude == 0:
                self._texture_pivot = (value[0], value[1], -1)
                return None
            self._texture_base_angle = diff.angle
            self._texture_base_offset = pg.Vector2(
                self._texture_pivot[0][0] - self._texture.width / 2,
                self._texture_pivot[0][1] - self._texture.height / 2,
            )

    def _tiles(self: Self, tilesize_inv: Real) -> None:
        tiles = set()
        top = math.inf
        bottom = -math.inf
        left = math.inf
        right = -math.inf
        for vertex in self._vertices:
            y = vertex._pos[1] - vertex._radius
            if y < top:
                top = y
            y = vertex._pos[1] + vertex._radius
            if y > bottom:
                bottom = y
            x = vertex._pos[0] - vertex._radius
            if x < left:
                left = x
            x = vertex._pos[0] + vertex._radius
            if x > right:
                right = x
        for y in range(
            math.floor(top * tilesize_inv),
            math.floor(bottom * tilesize_inv) + 1,
        ):
            for x in range(
                math.floor(left * tilesize_inv),
                math.floor(right * tilesize_inv) + 1,
            ):
                tiles.add((x, y))
        self._last_tiles = tiles
        return tiles

    def _collide_circle(self: Self, obj: Circle) -> None:
        for connection in self._connections:
            if not connection[2]:
                continue
            # https://stackoverflow.com/a/1501725/24845999
            # projects point onto line segment
            # vector projection formula but 
            # without final multiplication
            # then calculates distance to that point
            vertex1 = self._vertices[connection[0]]
            vertex2 = self._vertices[connection[1]]
            diff = vertex2._pos - vertex1._pos
            t = pg.math.clamp(
                diff.dot(obj._pos - vertex1._pos) / diff.magnitude_squared(),
                0, 1,
            )
            proj = vertex1._pos + t * diff
            diff = proj - obj._pos
            cur_dist = diff.magnitude()
            if 0 < cur_dist < obj._radius:
                dist = cur_dist - obj._radius
                if not (
                    obj._fixed or (vertex1._fixed and vertex2._fixed)
                ):
                    dist *= 0.5
                rel = diff / cur_dist * dist
                avg = 0
                count = 0
                if not obj._fixed:
                    avg += obj._mass_inv
                    count += 1
                if not vertex1._fixed:
                    avg += vertex1._mass_inv
                    count += 1
                if not vertex2._fixed:
                    avg += vertex2._mass_inv
                    count += 1
                if avg:
                    avg /= count
                    # not perfect collision resolution but good enough
                    if not obj._fixed:
                        # obj._pos += rel * obj._mass_inv / avg
                        obj._pos += rel
                    if not vertex1._fixed:
                        vertex1._pos -= (
                            rel * vertex1._mass_inv / avg * (1 - t) * 2
                        )
                    if not vertex2._fixed:
                        vertex2._pos -= (
                            rel * vertex2._mass_inv / avg * t * 2
                        )

    def _constrain(self: Self, objects: set[Object]) -> None:
        for obj in objects:
            if obj is self:
                continue
            if Circle in self._whitelist and isinstance(obj, Circle):
                self._collide_circle(obj)
            if Gon in self._whitelist and isinstance(obj, Gon):
                for vertex in obj._vertices:
                    self._collide_circle(vertex)
        for i in range(self._stiffness):
            deltas = {}
            for dex, connection in enumerate(self._connections):
                diff = (
                    self._vertices[connection[1]]._pos
                    - self._vertices[connection[0]]._pos
                )
                cur_dist = diff.magnitude()
                dist = cur_dist - self._dists[dex]
                if not (
                    self._vertices[connection[0]]._fixed
                    or self._vertices[connection[1]]._fixed
                ):
                    dist *= 0.5
                if cur_dist:
                    rel = diff / cur_dist * dist
                    if not self._vertices[connection[0]]._fixed:
                        if self._average:
                            vector = deltas.get(connection[0])
                            if vector is None:
                                deltas[connection[0]] = [rel, 1]
                            else:
                                vector[0] += rel
                                vector[1] += 1
                        else:
                            self._vertices[connection[0]]._pos += (
                                rel * self._vertices[connection[0]]._mass_inv
                            )
                    if not self._vertices[connection[1]]._fixed:
                        if self._average:
                            vector = deltas.get(connection[1])
                            if vector is None:
                                deltas[connection[1]] = [-rel, 1]
                            else:
                                vector[0] -= rel
                                vector[1] += 1
                        else:
                            self._vertices[connection[1]]._pos -= (
                                rel * self._vertices[connection[1]]._mass_inv
                            )
            for dex, delta in deltas.items():
                self._vertices[dex]._pos += (
                    delta[0] / delta[1] * self._vertices[dex]._mass_inv
                )

    def update(self: Self,
               timestep_sq: Real,
               objects: set[Object],
               force: pg.Vector2=(0, 0)) -> None:
        for vertex in self._vertices:
            vertex.update(timestep_sq, objects, self._force + force)
        self._constrain(objects)

    def render(self: Self, surf: pg.Surface, t: Real=1) -> None:
        if self._texture is None:
            for vertex in self._vertices:
                vertex.render(surf, t)
            for connection in self._connections:
                color = (255, 255, 255) if connection[2] else (0, 0, 255)
                pg.draw.line(
                    surf,
                    color,
                    self._vertices[connection[0]]._pos,
                    self._vertices[connection[1]]._pos,
                )
        elif self._texture_pivot is not None:
            if self._texture_pivot[1] != -1:
                diff = (
                    self._vertices[self._texture_pivot[2]]._pos
                    - self._vertices[self._texture_pivot[1]]._pos
                )
                angle = diff.angle - self._texture_base_angle
                scale = diff.magnitude() / self._texture_base_magnitude
                texture = pg.transform.rotate(
                    pg.transform.scale(
                        self._texture,
                        (self._texture.width * scale,
                         self._texture.height * scale)
                    ),
                    -angle,
                )
                offset = self._texture_base_offset.rotate(angle)
                surf.blit(
                    texture,
                    self._vertices[self._texture_pivot[1]]._pos
                    - (texture.width / 2, texture.height / 2)
                    - offset,
                )
            else:
                surf.blit(
                    self._texture,
                    self._vertices[self._texture_pivot[1]]._pos
                    - self._texture_pivot[0],
                )


KEY = { # key used when loading level files
    'object': Object,
    'circle': Circle,
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
            for tile in obj._tiles(self._tilesize_inv):
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

