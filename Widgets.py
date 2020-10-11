from abc import ABC, abstractmethod
from typing import List, Tuple, Callable

import pygame


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WidgetCmp(ABC):
    def __init__(self, screen: pygame.Surface, rect: pygame.Rect):
        self.screen = screen
        self.rect = rect

    @abstractmethod
    def __contains__(self, p: Point) -> bool:
        p = self.get_local_point(p)
        return (
                self.rect.left < p.x < self.rect.right and
                self.rect.top < p.y < self.rect.bottom
        )

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def mouse_move(self, p: Point):
        pass

    @abstractmethod
    def l_down(self, p: Point) -> None:
        pass

    @abstractmethod
    def l_up(self, p: Point) -> None:
        pass

    def get_local_rect(self, rect: pygame.Rect) -> pygame.Rect:
        raise NotImplementedError()

    def get_local_point(self, p: Point) -> Point:
        raise NotImplementedError()

    def get_global_rect(self, rect: pygame.Rect) -> pygame.Rect:
        raise NotImplementedError()

    def get_global_point(self, p: Point) -> Point:
        raise NotImplementedError()


class Widget:
    def __init__(
            self,
            screen: pygame.Surface,
            rect: pygame.Rect,
            cmp: List[WidgetCmp] = None,
            color: Tuple[int, int, int] = None
    ):
        """
        :param rect: Panel rectangle in (left, top, right, bottom) format
        :param cmp: List of Widget components
        :param color: The base color of the widget
        """
        self.screen = screen
        self.rect = rect
        if cmp is None:
            self.cmp = list()
        else:
            self.cmp = cmp
            for e in self.cmp:
                e.get_local_rect = self.get_local_rect
                e.get_local_point = self.get_local_point
                e.get_global_rect = self.get_global_rect
                e.get_global_point = self.get_global_point
        self.color = color

    def __contains__(self, p: Point) -> bool:
        """
        Checks if the given point is within the panel

        :param p: point to check
        :return: boolean result
        """
        return (
                self.rect.left < p.x < self.rect.right and
                self.rect.top < p.y < self.rect.bottom
        )

    def resize(self, rect: pygame.Rect):
        # TODO: Resize widget components
        self.rect = rect

    def display(self) -> None:
        pygame.draw.rect(self.screen, self.color, self.rect)

        for e in self.cmp:
            e.display()

    def mouse_move(self, p: Point) -> None:
        for e in self.cmp:
            if p in e:
                e.mouse_move(p)
                return

    def l_down(self, p: Point) -> None:
        for e in self.cmp:
            if p in e:
                e.l_down(p)
                return

    def l_up(self, p: Point) -> None:
        for e in self.cmp:
            if p in e:
                e.l_up(p)
                return

    def get_local_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            rect.left - self.rect.left,
            rect.top - self.rect.top,
            rect.width,
            rect.height
        )

    def get_local_point(self, p: Point) -> Point:
        return Point(
            p.x - self.rect.left,
            p.y - self.rect.top
        )

    def get_global_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            self.rect.left + rect.left,
            self.rect.top + rect.top,
            rect.width,
            rect.height
        )

    def get_global_point(self, p: Point) -> Point:
        return Point(
            self.rect.left + p.x,
            self.rect.top + p.y
        )


class EyePromptWidget(Widget):
    def __init__(self, screen: pygame.Surface, rect: pygame.Rect):
        super().__init__(screen, rect)

    def display(self) -> None:
        pass

    def start(self) -> None:
        pass
