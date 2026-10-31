import time
import math
from typing import Self

import pygame as pg

from modules.physics import Circle
from modules.physics import Gon
from modules.physics import Level
from modules.presets import preset


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
                texture=pg.image.load('circle.png').convert_alpha(),
            ))
        objects.add(Circle(
            (8, 8),
            radius=8,
            mass=4,
        ))
        objects.add(Circle(
            (8, 16),
            radius=4,
            mass=1,
        ))
        radius = 0
        """
        objects.add(Gon(
            (Circle((210, 210), radius, fixed=0),
             Circle((250, 210), radius, fixed=0),
             Circle((250, 250), radius, fixed=0),
             Circle((210, 250), radius, fixed=0)),
            ((0, 2, 0), (1, 3, 0), (0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)),
            # texture=pg.image.load('square.png').convert_alpha(),
            texture_pivot=((0, 0), 0, 2),
        ))
        """
        objects.add(preset('triangle_up_left', (100, 100), fixed=1))
        """objects.add(preset('pinwheel', (180, 135)))"""
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

