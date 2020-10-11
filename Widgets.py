from abc import ABC, abstractmethod
from typing import List, Tuple, Callable

import pygame


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WidgetCmp(ABC):
    @abstractmethod
    def __contains__(self, p: Point) -> bool:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def l_down(self) -> None:
        pass

    @abstractmethod
    def l_up(self) -> None:
        pass

    @abstractmethod
    def l_release(self) -> None:
        pass

    def get_global_coords(self, rect: pygame.Rect) -> pygame.Rect:
        raise NotImplementedError()


class Widget(ABC):
    def __init__(
            self,
            screen: pygame.Surface,
            rect: pygame.Rect,
            cmp: List[WidgetCmp] = None,
            color: Tuple[int] = None
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
                e.get_global_coords = self.get_global_coords
        self.color = color

    def __contains__(self, p: Point) -> bool:
        """
        Checks if the given point is within the panel

        :param p: point to check
        :return: boolean result
        """
        if (
                self.rect.left < p.x < self.rect.right and
                self.rect.top < p.y < self.rect.bottom
        ):
            return True
        return False

    def display(self) -> None:
        pygame.draw.rect(self.screen, self.color, self.rect)

        for e in self.cmp:
            e.display()

    @abstractmethod
    def l_down(self) -> None:
        pass

    @abstractmethod
    def l_up(self) -> None:
        pass

    @abstractmethod
    def l_release(self) -> None:
        pass

    def get_global_coords(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            self.rect.left + rect.left,
            self.rect.top + rect.top,
            rect.width,
            rect.height
        )


class EyePromptWidget(Widget):
    def __init__(self, screen: pygame.Surface, rect: pygame.Rect):
        super().__init__(screen, rect)

    def display(self) -> None:
        pass

    def l_down(self) -> None:
        pass

    def l_up(self) -> None:
        pass

    def l_release(self) -> None:
        pass
