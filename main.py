import os

from Widgets import *


class Palette:
    background = (0, 0, 150)
    widget = (50, 50, 50)


def onPaint(screen, panels: List[Widget]):
    screen.fill(Palette.background)

    p = pygame.mouse.get_pos()
    for e in panels:
        if p in e:
            e.display()


def main():
    # pygame initialization
    pygame.init()
    info = pygame.display.Info()
    screenSize = (info.current_w, info.current_h)

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (screenSize[0]//16, screenSize[1]//16)
    icon = pygame.image.load("./assets/HSL-32.png")
    pygame.display.set_icon(icon)

    screen = pygame.display.set_mode((14*screenSize[0]//16, 14*screenSize[1]//16), flags=pygame.RESIZABLE)
    pygame.display.set_caption("HSL | Eye Tracking Data Collection")

    # widget initialization


    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.VIDEORESIZE:
                screen.fill(Palette.background)
                screen = pygame.display.set_mode(event.size, flags=pygame.RESIZABLE)

        onPaint(screen, [])
        pygame.display.flip()


if __name__ == "__main__":
    main()
