# import PyWorldSim.src.worldsim
import pygame


class Application(object):
    color_black = pygame.Color(0, 0, 0)

    def __init__(self):
        self.screen = None

    def launch(self, width=500, height=425):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(Application.color_black)
        pygame.display.flip()

    def close(self):
        pygame.display.quit()
