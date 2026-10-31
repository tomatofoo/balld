import copy
from typing import Self
from typing import Optional
from numbers import Real

import pygame as pg

from modules.physics import Object
from modules.physics import Gon
from modules.physics import Circle


PRESETS = {
    'ball': {'obj': Circle((0, 0), 0, fixed=0)},
    'triangle_up_left': {
        'obj': Gon(
            (Circle((-20,  -20), 0, fixed=0),
             Circle((20,   20), 0, fixed=0),
             Circle((-20, 20), 0, fixed=0)),
            ((0, 1, 1), (1, 2, 1), (0, 2, 1)),
        ),
        'pivot': (0, 1),
    },
    'triangle_down_left': {
        'obj': Gon(
            (Circle((20,  -20), 0, fixed=0),
             Circle((20,   20), 0, fixed=0),
             Circle((-20, -20), 0, fixed=0)),
            ((0, 1, 1), (1, 2, 1), (0, 2, 1)),
        ),
        'pivot': (0, 1),
    },
    'pinwheel': {
        'obj': Gon(
            (Circle((0,    0), 0, fixed=1),
             Circle((-5,  -5), 0, fixed=0),
             Circle((5,   -5), 0, fixed=0),
             Circle((5,    5), 0, fixed=0),
             Circle((-5,   5), 0, fixed=0),
             Circle((-5, -55), 0, fixed=0),
             Circle((5,  -55), 0, fixed=0),
             Circle((-5,  55), 0, fixed=0),
             Circle((5,   55), 0, fixed=0),
             Circle((-55, -5), 0, fixed=0),
             Circle((-55,  5), 0, fixed=0),
             Circle((55,  -5), 0, fixed=0),
             Circle((55,   5), 0, fixed=0)),
            ((0, 1,  0), (0, 2, 0),  (0,  3,  0), (0,  4,  0),
             (1, 2,  0), (2, 3, 0),  (3,  4,  0), (4,  1,  0),
             (5, 8,  0), (6, 7, 0),  (9,  12, 0), (10, 11, 0),
             (5, 7,  0), (6, 8, 0),  (9,  11, 0), (10, 12, 0),
             (5, 9,  0), (6, 11, 0), (7,  10, 0), (8,  12, 0),
             (5, 6,  1), (1, 5,  1), (2,  6,  1), 
             (3, 8,  1), (4, 7,  1), (7,  8,  1),
             (1, 9,  1), (4, 10, 1), (9,  10, 1),
             (2, 11, 1), (3, 12, 1), (11, 12, 1)),
            stiffness=5,
        ),
        'pivot': (0, 5),
    },
}

def preset(key: str,
           pos: pg.Vector2,
           radius: Real=None,
           fixed: bool=0,
           texture: Optional[pg.Surface]=None,
           texture_pos: Optional[pg.Vector2]=None) -> Object:
    item = PRESETS[key]
    obj = copy.deepcopy(item['obj'])
    obj._pos += pos
    obj._prev_pos += pos
    obj._fixed = fixed
    obj._texture = texture
    if isinstance(obj, Circle):
        if radius is not None:
            vertex._radius = radius
    elif isinstance(obj, Gon):
        for vertex in obj._vertices:
            vertex._pos += pos
            vertex._prev_pos += pos
            if radius is not None:
                vertex._radius = radius
        pivot = item['pivot']
        obj.texture_pivot = (texture_pos, pivot[0], pivot[1])

    return obj

