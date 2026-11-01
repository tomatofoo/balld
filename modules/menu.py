from typing import Self
from typing import Optional
from typing import Callable

import pygame as pg
from pygame.typing import Point


class Element(object):
    def __init__(self: Self, pos: Point) -> None:
        self._pos = pos
        self._rect = pg.Rect(0, 0, 0, 0)

    @property
    def pos(self: Self) -> Point:
        return self._pos

    @pos.setter
    def pos(self: Self, value: Point) -> None:
        self._pos = value
        self._rect.center = value

    def handle_event(self: Self, event: pg.Event) -> None:
        pass

    def update(self: Self, mouse_pos: Point, mouse_pressed: tuple[bool]) -> None:
        pass

    def render(self: Self, surf: pg.Surface) -> None:
        pass


class Text(Element):
    def __init__(self: Self, pos: Point, text: str, font: pg.Font) -> None:
        super().__init__(pos)
        self._font = font
        self.text = text

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value
        self._surf = self._font.render(self._text, 0, (255, 255, 255))
        self._rect = pg.Rect((0, 0), self._surf.size)
        self._rect.center = self._pos

    def render(self: Self, surf: pg.Surface) -> None:
        surf.blit(self._surf, (self._rect.x, self._rect.y))


class Button(Element):
    def __init__(self: Self,
                 pos: Point,
                 text: str,
                 font: pg.Font,
                 func: Callable = lambda arg: None,
                 arg: object=None,
                 enabled: bool=1) -> None:
        super().__init__(pos)
        self._font = font
        self.text = text
        self._func = func
        self._arg = arg
        self._enabled = enabled
        self._state = 'default'

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value
        rendered = self._font.render(self._text, 0, (255, 255, 255))
        size = rendered.get_rect().inflate(5, 5).size
        pos = ((size[0] - rendered.width) / 2, (size[1] - rendered.height) / 2)
        self._surfs = {
            'default': pg.Surface(size),
            'hover': pg.Surface(size),
            'click': None,
        }
        self._surfs['default'].fill((0, 0, 255))
        self._surfs['default'].blit(rendered, pos)
        self._surfs['hover'].fill((255, 0, 0))
        self._surfs['hover'].blit(rendered, pos)
        self._surfs['click'] = self._surfs['hover'].copy()
        pg.draw.rect(self._surfs['click'], (255, 255, 255), ((0, 0), size), 1)
        self._overlay = pg.Surface(size)
        self._overlay.set_alpha(128)
        self._rect = pg.Rect((0, 0), size)
        self._rect.center = self._pos

    @property
    def enabled(self: Self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self: Self, value: bool) -> None:
        self._enabled = value

    def handle_event(self: Self, event: pg.Event) -> None:
        if not self._enabled:
            return
        if (event.type == pg.MOUSEBUTTONDOWN
            and self._rect.collidepoint(self._mouse_pos)):
            self._func(self._arg)

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        self._mouse_pos = mouse_pos
        if not self._enabled:
            self._state = 'default'
            return
        if self._rect.collidepoint(mouse_pos):
            self._state = 'click' if mouse_pressed[0] else 'hover'
        else:
            self._state = 'default'

    def render(self: Self, surf: pg.Surface) -> None:
        rendered = self._surfs[self._state]
        surf.blit(rendered, (self._rect.x, self._rect.y)) 
        if not self._enabled:
            surf.blit(self._overlay, (self._rect.x, self._rect.y))


class Draggable(Element):
    def __init__(self: Self,
                 pos: Point,
                 surf: pg.Surface,
                 drag_surf: Optional[pg.Surface]=None,
                 drag_func: Callable=lambda arg, pos: None,
                 release_func: Callable=lambda arg, pos: None,
                 arg: object=None,
                 enabled: bool=1) -> None:
        super().__init__(pos)
        self._surf = surf.copy()
        self._drag_surf = surf.copy()
        if drag_surf is not None:
            self._drag_surf = drag_surf
        self._rect = pg.Rect((0, 0), surf.size)
        self._rect.center = pos
        self._dragging = 0
        self._drag_func = drag_func
        self._release_func = release_func
        self._arg = arg
        self._mouse_pos = (0, 0)
        self._enabled = enabled

    @property
    def arg(self: Self) -> str:
        return self._arg

    @arg.setter
    def arg(self: Self, value: str) -> None:
        self._arg = value

    @property
    def enabled(self: Self) -> None:
        return self._enabled

    @enabled.setter
    def enabled(self: Self, value: bool) -> None:
        self._enabled = value

    def handle_event(self: Self, event: pg.Event) -> None:
        if (event.type == pg.MOUSEBUTTONDOWN
            and self._rect.collidepoint(self._mouse_pos)
            and self._enabled):
            self._dragging = 1
            self._drag_func(self._arg, self._mouse_pos)
        elif event.type == pg.MOUSEBUTTONUP and self._dragging:
            self._dragging = 0
            self._release_func(self._arg, self._mouse_pos)

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        self._mouse_pos = mouse_pos

    def render(self: Self, surf: pg.Surface) -> None:
        if self._dragging:
            pos = self._mouse_pos - pg.Vector2(self._drag_surf.size) / 2
            surf.blit(self._drag_surf, pos)
        if self._enabled:
            self._surf.set_alpha(None)
        else:
            self._surf.set_alpha(128)
        surf.blit(self._surf, (self._rect.x, self._rect.y))


class Menu(object):
    def __init__(self: Self, elems: set[Element]=set()) -> None:
        self._elems = elems

    @property
    def elems(self: Self) -> set[Element]:
        return self._elems

    @elems.setter
    def elems(self: Self, value: set[Element]) -> None:
        self._elems = value

    def handle_event(self: Self, event: pg.Event) -> None:
        for elem in self._elems:
            elem.handle_event(event)
    
    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        for elem in self._elems:
            elem.update(mouse_pos, mouse_pressed)

    def render(self: Self, surf: pg.Surface) -> None:
        for elem in self._elems:
            elem.render(surf)

