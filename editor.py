import time
import math
import json
from typing import Self

import pygame as pg
from pygame.typing import Point

from modules.menu import Text
from modules.menu import Button
from modules.menu import Draggable
from modules.menu import Menu
from modules.physics import Circle
from modules.physics import Gon
from modules.physics import Level
from modules.presets import PRESETS
from modules.presets import render_preset
from modules.presets import preset


class Game(object):

    _SCREEN_SIZE = (720, 540)
    _SURF_RATIO = (2, 2)
    _SURF_SIZE = (int(_SCREEN_SIZE[0] / _SURF_RATIO[0]),
                  int(_SCREEN_SIZE[1] / _SURF_RATIO[1]))
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 1
    _TIMEOUT = 1
    _TRY_TIMEOUT = 10

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

        self._FONT = pg.font.SysFont('Arial', 10)
        
        self._frame = {
            Gon(
                (Circle((0,     0), 0),
                 Circle((0,   270), 0),
                 Circle((280,   0), 0),
                 Circle((280, 270), 0),
                 Circle((120,  60), 0),
                 Circle((160,  60), 0),
                 Circle((0,    40), 0),
                 Circle((280,  40), 0)),
                ((0, 1, 1), (2, 3, 1),
                 (4, 6, 1), (5, 7, 1)),
                fixed=1,
            ),
        }
        self._objects = self._frame.copy()
        self._level = Level(self._objects, tilesize=8)

        self._MENU_WIDTH = 80
        self._LEFT = 0
        self._RIGHT = self._SURF_SIZE[0] - self._MENU_WIDTH

        self._number = 1

        self._button_save = Button(
            (self._RIGHT + self._MENU_WIDTH / 2, 20),
            'Save',
            self._FONT,
            self._save,
        )
        self._button_load = Button(
            (self._RIGHT + self._MENU_WIDTH / 2, 45),
            'Load',
            self._FONT,
            self._load,
        )
        self._text_save = Text(
            (self._RIGHT + self._MENU_WIDTH / 2, 70),
            str(self._number),
            self._FONT,
        )
        self._base = {
            self._button_save,
            self._button_load,
            self._text_save,
        }
        self._renders = {}
        size = 20
        for key in PRESETS:
            self._renders[key] = [None, render_preset(key)]
            width = self._renders[key][1].width
            height = self._renders[key][1].height
            factor = size / height if width < height else size / width
            self._renders[key][0] = pg.transform.scale_by(
                self._renders[key][1], (factor, factor),
            )
        self._menu = Menu(set())

        self._balls = set()
        self._load()
        self._trying = 0
        self._timer = 0
        self._score = 0
        self._obj_count = len(self._objects)
        
    def _save(self: Self, arg: object=None) -> None:
        data = {
            'inventory': {},
            'obstacles': {},
            'win': [
                self._win[0] // 10 * 10,
                self._win[1] // 10 * 10,
                self._win[2] // 10 * 10,
                self._win[3] // 10 * 10
            ],
            'min': 10,
            'par': 10,
        }
        for obj in self._objects:
            key = f'{int(obj.pos[0] // 10 * 10)};{int(obj.pos[1] // 10 * 10)}'
            data['obstacles'][key] = obj.data
        with open(f'data/{self._number}.json', 'w') as file:
            self._stage = json.dump(data, file)
  
    def _load(self: Self, arg: object=None) -> None:
        with open(f'data/{self._number}.json', 'r') as file:
            self._stage = json.loads(file.read())
        self._inventory = self._stage['inventory'].copy()
        self._counters = {}
        self._objects = self._frame.copy()
        for pos, key in self._stage['obstacles'].items():
            split = pos.split(';')
            obj_pos = (int(split[0]), int(split[1]))
            self._objects.add(preset(key, obj_pos))
        self._win = pg.Rect(self._stage['win'])
        self._elems = self._base.copy()
        left = self._RIGHT + self._MENU_WIDTH / 4
        top = 100
        margin = self._MENU_WIDTH / 2
        counter_margin = margin - 25
        rowlen = 2
        for i, key in enumerate(PRESETS):
            pos = pg.Vector2(
                left + i % rowlen * margin,
                top + i // rowlen * margin,
            )
            self._elems.add(Draggable(
                pos,
                self._renders[key][0],
                self._renders[key][1],
                release_func=self._release,
                arg=key,
            ))
        self._level.objects = self._objects
        self._menu.elems = self._elems

    def _release(self: Self, arg: str, mouse_pos: Point) -> None:
        if mouse_pos[0] <= self._RIGHT:
            self._objects.add(preset(arg, mouse_pos))

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        dragging = None

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = min(delta_time * self._GAME_SPEED, self._TIMEOUT)

            mouse_pos = pg.Vector2(pg.mouse.get_pos())
            mouse_pos[0] /= self._SURF_RATIO[0]
            mouse_pos[1] /= self._SURF_RATIO[1]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_1:
                        self._number = 1
                    elif event.key == pg.K_2:
                        self._number = 2
                    elif event.key == pg.K_3:
                        self._number = 3
                    elif event.key == pg.K_4:
                        self._number = 4
                    elif event.key == pg.K_5:
                        self._number = 5
                    elif event.key == pg.K_6:
                        self._number = 6
                    elif event.key == pg.K_7:
                        self._number = 7
                    elif event.key == pg.K_8:
                        self._number = 8
                    elif event.key == pg.K_9:
                        self._number = 9
                    self._text_save.text = str(self._number)
                elif (event.type == pg.MOUSEBUTTONDOWN
                      and mouse_pos[0] <= self._RIGHT):
                    closest = [None, math.inf]
                    for obj in self._objects:
                        if obj not in self._frame:
                            dist = mouse_pos.distance_to(obj.pos)
                            if dist < closest[1]:
                                closest[0] = obj
                                closest[1] = dist
                    if closest[0] is not None:
                        self._objects.remove(closest[0])
                        dragging = closest[0].data
                elif event.type == pg.MOUSEBUTTONUP and dragging is not None:
                    self._release(dragging, mouse_pos)
                    dragging = None
                self._menu.handle_event(event)

            # Update
            self._menu.update(mouse_pos, pg.mouse.get_pressed())

            # Render
            self._surface.fill((0, 0, 0))
            self._level.render(self._surface)
            pg.draw.rect( # bg
                self._surface,
                (0, 0, 0),
                (self._RIGHT + 1, 0, self._MENU_WIDTH, self._SURF_SIZE[1]),
            )
            self._menu.render(self._surface)
            if dragging is not None: # dragging objects around
                surf = self._renders[dragging][1]
                self._surface.blit(
                    surf, mouse_pos - pg.Vector2(surf.size) / 2,
                )
            
            resized_surf = pg.transform.scale(self._surface, self._SCREEN_SIZE)
            self._screen.blit(resized_surf, (0, 0))

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

