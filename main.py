import time
import math
from typing import Self

import pygame as pg

from modules.physics import Circle
from modules.physics import Gon
from modules.physics import Level


class Game(object):

    _SCREEN_SIZE = (720, 540)
    _SURF_RATIO = (2, 2)
    _SURF_SIZE = (int(_SCREEN_SIZE[0] / _SURF_RATIO[0]),
                  int(_SCREEN_SIZE[1] / _SURF_RATIO[1]))
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 1
    _TIMEOUT = 1

    def __init__(self: Self) -> None:
        pg.init()

        self._settings = {
            'graphics': {
                'vsync': 1,
            },
        }
        self._screen = pg.display.set_mode(
            self._SCREEN_SIZE,
            flags=self._SCREEN_FLAGS,
            vsync=self._settings['graphics']['vsync']
        )
        pg.display.set_caption('Balld')
        self._surface = pg.Surface(self._SURF_SIZE)
        self._running = 0
        
        objects = set()
        length = 10
        for i in range(300):
            objects.add(Circle(
                (20 + i % length * 8, 20 + i // length * 8),
                radius=4,
                mass=1,
                force=pg.Vector2(0, 320),
                texture=pg.image.load('circle.png').convert_alpha(),
            ))
        objects.add(Circle(
            (8, 8),
            radius=8,
            mass=4,
            force=pg.Vector2(0, 1280),
        ))
        objects.add(Circle(
            (8, 16),
            radius=4,
            mass=1,
            force=pg.Vector2(0, 320),
        ))
        radius = 4
        objects.add(Gon(
            (Circle((210, 210), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((250, 210), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((250, 250), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((210, 250), radius, force=pg.Vector2(0, 320), fixed=0)),
            ((0, 2, 0), (1, 3, 0), (0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)),
            # texture=pg.image.load('square.png').convert_alpha(),
            texture_pivot=((0, 0), 0, 2),
        ))
        objects.add(Gon(
            (Circle((150,  60), radius, force=pg.Vector2(0, 320), fixed=1),
             Circle((150, 100), radius, force=pg.Vector2(0, 320), fixed=1),
             Circle((110, 100), radius, force=pg.Vector2(0, 320), fixed=1)),
            ((0, 1, 1), (1, 2, 1), (0, 2, 1)),
        ))
        # THE BEHEMOTH
        objects.add(Gon(
            (Circle((180, 135), radius, force=pg.Vector2(0, 320), fixed=1),
             Circle((175, 130), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 130), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 140), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((175, 140), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((175,  80), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((185,  80), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((175, 190), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 190), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((125, 130), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((125, 140), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((235, 130), radius, force=pg.Vector2(0, 320), fixed=0),
             Circle((235, 140), radius, force=pg.Vector2(0, 320), fixed=0)),
            ((0, 1,  0), (0, 2, 0),  (0, 3,  0), (0,  4,  0),
             (1, 2,  0), (2, 3, 0),  (3, 4,  0), (4,  1,  0),
             (5, 8,  0), (6, 7, 0),  (9, 12, 0), (10, 11, 0),
             (5, 7,  0), (6, 8, 0),  (9, 11, 0), (10, 12, 0),
             # (1, 6,  0), (2, 5, 0),  (3, 7,  0), (4,  8,  0),
             # (1, 10, 0), (4, 9, 0),  (2, 12, 0), (3,  11, 0),
             (5, 9,  0), (6, 11, 0), (7,  10, 0), (8, 12, 0),
             # (5, 11, 0), (6, 9,  0), (7,  12, 0), (8, 10, 0),
             (5, 6,  1), (1, 5,  1), (2,  6,  1), 
             (3, 8,  1), (4, 7,  1), (7,  8,  1),
             (1, 9,  1), (4, 10, 1), (9,  10, 1),
             (2, 11, 1), (3, 12, 1), (11, 12, 1)),
            stiffness=5,
            texture=pg.image.load('wheel.png').convert_alpha(),
            texture_pivot=((55, 55), 0, 5),
        ))
        self._level = Level(objects, tilesize=8)

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        clicking = None

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = min(delta_time * self._GAME_SPEED, self._TIMEOUT)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                # TEMP
                if event.type == pg.MOUSEBUTTONDOWN:
                    pos = (event.pos[0] / 2, event.pos[1] / 2)
                    for obj in self._level.objects:
                        if isinstance(obj, Circle):
                            if obj.pos.distance_to(pos) < obj.radius:
                                clicking = [obj, obj.fixed]
                        elif isinstance(obj, Gon):
                            for vertex in obj.vertices:
                                if vertex.pos.distance_to(pos) <= vertex.radius:
                                    clicking = [vertex, vertex.fixed]
                elif event.type == pg.MOUSEMOTION and clicking is not None:
                    clicking[0].pos = event.pos[0] / 2, event.pos[1] / 2
                    clicking[0].fixed = 1
                elif event.type == pg.MOUSEBUTTONUP and clicking is not None:
                    clicking[0].fixed = clicking[1]
                    clicking = None
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_f and clicking is not None:
                        clicking[1] = not clicking[1]

            # Update
            self._level.update(rel_game_speed)

            # Render
            self._surface.fill((0, 0, 0))
            self._level.render(self._surface)
            
            resized_surf = pg.transform.scale(self._surface, self._SCREEN_SIZE)
            self._screen.blit(resized_surf, (0, 0))

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

