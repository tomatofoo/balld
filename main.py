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
                 Circle((280,  40), 0),
                 Circle((120, 200), 0),
                 Circle((160, 200), 0),
                 Circle((140, 180), 0)),
                ((0, 1, 1), (2, 3, 1),
                 (4, 6, 1), (5, 7, 1),
                 (8, 9, 1), (8, 10, 1), (9, 10, 1)),
                fixed=1,
            ),
        }
        self._objects = self._frame.copy()
        self._level = Level(self._objects, tilesize=8)

        self._MENU_WIDTH = 80
        self._LEFT = 0
        self._RIGHT = self._SURF_SIZE[0] - self._MENU_WIDTH
        
        self._button_try = Button(
            (self._RIGHT + self._MENU_WIDTH / 2, 20),
            'Try',
            self._FONT,
            self._try,
        )
        self._button_cancel = Button(
            (self._RIGHT + self._MENU_WIDTH / 2, 45),
            'Cancel',
            self._FONT,
            self._cancel,
            enabled=0,
        )
        self._button_reset = Button(
            (self._RIGHT + self._MENU_WIDTH / 2, 70),
            'Reset',
            self._FONT,
            self._reset,
        )

        self._base = {
            self._button_try,
            self._button_cancel,
            self._button_reset,
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
        
        self._text_score = Text((180, 45), '0', self._FONT)
        self._text_min = Text((180, 70), '0', self._FONT)
        self._text_par = Text((180, 95), '0', self._FONT)
        self._win_menu = Menu({
            Text((180, 20), 'You Beat the Level!', self._FONT),
            self._text_score,
            self._text_min,
            self._text_par,
            Button((180, 240), 'Next', self._FONT, self._next),
        })

        self._text_total_score = Text((180, 45), '0', self._FONT)
        self._finish_menu = Menu({
            Text((180, 20), 'You Finished!', self._FONT),
            self._text_total_score,
            Button((180, 240), 'Restart', self._FONT, self._restart),
        })
        
        self._victory = 0
        self._finish = 0
        self._balls = set()
        self._number = 1
        self._amount = 1
        self._load(self._number)
        self._score = 0
        self._total_score = 0
        self._trying = 0
        self._timer = 0
        self._obj_count = len(self._objects)
        
    def _load(self: Self, number: int) -> None:
        with open(f'data/{number}.json', 'r') as file:
            self._stage = json.loads(file.read())
        self._inventory = self._stage['inventory'].copy()
        self._counters = {}
        self._objects = self._frame.copy()
        for pos_key, key in self._stage['obstacles'].items():
            split = pos_key.split(';')
            pos = pg.Vector2(int(split[0]), int(split[1]))
            self._objects.add(preset(key, pos))
        self._win = pg.Rect(self._stage['win'])
        self._elems = self._base.copy()
        left = self._RIGHT + self._MENU_WIDTH / 4
        top = 100
        margin = self._MENU_WIDTH / 2
        counter_margin = margin - 25
        rowlen = 2
        for i, (key, count) in enumerate(self._inventory.items()):
            pos = pg.Vector2(
                left + i % rowlen * margin,
                top + i // rowlen * margin,
            )
            self._elems.add(Draggable(
                pos,
                self._renders[key][0],
                self._renders[key][1],
                self._drag,
                self._release,
                key,
            ))
            self._counters[key] = Text(
                pos + (0, counter_margin),
                str(count),
                self._FONT,
            )
            self._elems.add(self._counters[key])
        self._level.objects = self._objects
        self._menu.elems = self._elems

    def _try(self: Self, arg: object=None) -> None:
        self._score = 0
        self._button_try.enabled = 0
        self._button_cancel.enabled = 1
        self._button_reset.enabled = 0
        for elem in self._elems:
            if isinstance(elem, Draggable):
                elem.enabled = 0
        self._obj_count = len(self._objects)
        self._trying = 1
        self._timer = 0
        self._menu.update((math.inf, math.inf), (0, 0, 0))
        period = 10
        self._balls = set()
        for i in range(10):
            self._balls.add(Circle((self._LEFT + 10, -10 - i * period), 4))
        for i in range(10):
            self._balls.add(Circle((self._RIGHT - 10, -10 - i * period), 4))
        self._objects |= self._balls

    def _cancel(self: Self, arg: object=None) -> None:
        self._trying = 0
        self._button_try.enabled = 1
        self._button_cancel.enabled = 0
        self._button_reset.enabled = 1
        for elem in self._elems:
            if isinstance(elem, Draggable) and self._inventory[elem.arg] > 0:
                elem.enabled = 1
        self._timer = 0 # so drag doesn't reset it
        for ball in self._balls:
            if ball in self._objects:
                self._objects.remove(ball)

    def _reset(self: Self, arg: object=None) -> None:
        self._inventory = self._stage['inventory'].copy()
        self._objects = self._frame.copy()
        self._level.objects = self._objects
        for elem in self._elems:
            if isinstance(elem, Draggable):
                elem.enabled = 1

    def _drag(self: Self, arg: str, mouse_pos: Point) -> None:
        self._inventory[arg] -= 1
        self._counters[arg].text = str(self._inventory[arg])
        if self._inventory[arg] <= 0:
            for elem in self._elems:
                if isinstance(elem, Draggable) and elem.arg == arg:
                    elem.enabled = 0

    def _release(self: Self, arg: str, mouse_pos: Point) -> None:
        if mouse_pos[0] > self._RIGHT:
            self._inventory[arg] += 1
            self._counters[arg].text = str(self._inventory[arg])
            for elem in self._elems:
                if isinstance(elem, Draggable) and elem.arg == arg:
                    elem.enabled = 1
        else:
            self._objects.add(preset(arg, mouse_pos))

    def _next(self: Self, arg: object=None) -> None:
        self._number += 1
        if self._number <= self._amount:
            self._load(self._number)
            self._victory = 0
            self._score = 0
        else:
            self._finish = 1
            self._text_total_score.text = (
                f'Total Score: {self._total_score}/{20 * self._amount}'
            )

    def _restart(self: Self, arg: object=None) -> None:
        self._victory = 0
        self._finish = 0
        self._balls = set()
        self._number = 1
        self._amount = 5
        self._load(self._number)
        self._score = 0
        self._trying = 0
        self._timer = 0
        self._obj_count = len(self._objects)

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
                elif self._finish:
                    self._finish_menu.handle_event(event)
                elif self._victory:
                    self._win_menu.handle_event(event)
                else:
                    if (event.type == pg.MOUSEBUTTONDOWN
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
            if self._finish:
                self._finish_menu.update(mouse_pos, pg.mouse.get_pressed())
            elif self._victory:
                self._win_menu.update(mouse_pos, pg.mouse.get_pressed())
            else:
                if self._trying:
                    self._timer += rel_game_speed
                    self._level.update(rel_game_speed)
                    remove = set()
                    for obj in self._objects:
                        if isinstance(obj, Circle):
                            if self._win.collidepoint(obj.pos):
                                remove.add(obj)
                                self._score += 1
                            elif obj.pos[1] > self._surface.height + obj.radius:
                                remove.add(obj)
                    for obj in remove:
                        self._objects.remove(obj)
                    if (len(self._objects) <= self._obj_count
                        or self._timer > self._TRY_TIMEOUT):
                        self._cancel()
                        if self._score >= self._stage['min']:
                            self._total_score += self._score
                            self._victory = 1
                            self._text_score.text = f'Score: {self._score}'
                            self._text_min.text = f'Min Score: {self._stage['min']}'
                            self._text_par.text = f'Par Score: {self._stage['par']}'
                self._menu.update(mouse_pos, pg.mouse.get_pressed())

            # Render
            self._surface.fill((0, 0, 0))
            if self._finish:
                self._finish_menu.render(self._surface)
            elif self._victory:
                self._win_menu.render(self._surface)
            else:
                self._level.render(self._surface)
                pg.draw.rect(self._surface, (0, 255, 0), self._win, 2)
                pg.draw.rect( # menu bg
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
                text = self._FONT.render(
                    f'Score: {self._score}', 0, (255, 255, 255),
                )
                self._surface.blit(text, (2, 1))
                text = self._FONT.render(
                    f'Min Score: {self._stage['min']}', 0, (255, 255, 255),
                )
                self._surface.blit(text, (2, 14))
            
            resized_surf = pg.transform.scale(self._surface, self._SCREEN_SIZE)
            self._screen.blit(resized_surf, (0, 0))

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

