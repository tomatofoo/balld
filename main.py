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
        for i in range(300):
            objects.add(Circle((2 + i * 2, 20), 4, force=pg.Vector2(0, 320)))
        objects.add(Gon(
            (Circle((210, 210), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((250, 210), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((250, 250), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((210, 250), 2, force=pg.Vector2(0, 320), fixed=0)),
            ((0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)),
        ))
        objects.add(Gon(
            (Circle((150, 60), 2, force=pg.Vector2(0, 320), fixed=1),
             Circle((150, 100), 2, force=pg.Vector2(0, 320), fixed=1),
             Circle((110, 100), 2, force=pg.Vector2(0, 320), fixed=1)),
            ((0, 1), (1, 2), (0, 2)),
        ))
        """
        # THE BEHEMOTH
        objects.add(Gon(
            (Circle((180, 135), 2, force=pg.Vector2(0, 320), fixed=1),
             Circle((175, 130), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 130), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 140), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((175, 140), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((175, 80), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 80), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((175, 190), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((185, 190), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((125, 130), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((125, 140), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((235, 130), 2, force=pg.Vector2(0, 320), fixed=0),
             Circle((235, 140), 2, force=pg.Vector2(0, 320), fixed=0)),
            ((0, 1), (0, 2), (0, 3), (0, 4),
             (1, 2), (2, 3), (3, 4), (4, 1),
             (1, 5), (2, 6), (1, 6), (2, 5), (5, 6),
             (3, 7), (4, 8), (3, 8), (4, 7), (7, 8),
             (1, 9), (4, 10), (1, 10), (4, 9), (9, 10),
             (2, 12), (3, 11), (2, 11), (3, 12), (11, 12),
             (5, 8), (6, 7), (9, 12), (10, 11),
             (5, 7), (6, 8), (9, 11), (10, 12)),
            stiffness=20,
        ))
        """
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
                                if vertex.pos.distance_to(pos) < vertex.radius:
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

