from abc import ABC, abstractmethod
from typing import List, Tuple

import pygame

pAP = None
background = (0, 0, 0)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Panel(ABC):
    def __init__(self, rect: pygame.Rect):
        """
        :param rect: Panel rectangle in (left, top, right, bottom) format
        """
        self.rect = rect

    @abstractmethod
    def __contains__(self, p: Point):
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


def onPaint(screen, panels: List[Panel]):
    screen.fill(background)

    p = pygame.mouse.get_pos()
    for e in panels:
        if p in e:
            e.display()


def main():
    screen = pygame.display.set_mode(flags=pygame.RESIZABLE)
    pygame.display.set_caption("HMS : Eye Tracking Data Collection")

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.VIDEORESIZE:
                screen.fill(background)
                screen = pygame.display.set_mode(event.size, flags=pygame.RESIZABLE)

        onPaint(screen, [])
        pygame.display.flip()


if __name__ == "__main__":
    main()
