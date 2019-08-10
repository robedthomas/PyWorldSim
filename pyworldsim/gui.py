from pyworldsim import worldsim
import pygame


class Application(object):
    color_black = pygame.Color(0, 0, 0)
    color_gray = pygame.Color(183, 194, 255)
    color_brown = pygame.Color(127, 51, 0)
    color_blue = pygame.Color(38, 88, 255)
    color_green = pygame.Color(83, 124, 0)
    color_yellow = pygame.Color(255, 229, 0)
    color_orange = pygame.Color(255, 148, 0)
    color_red = pygame.Color(255, 42, 0)
    terrain_colors = {worldsim.space_type_riverland: color_green,
                      worldsim.space_type_grassland: color_yellow,
                      worldsim.space_type_dryland:   color_orange,
                      worldsim.space_type_hill:      color_red,
                      worldsim.space_type_mountain:  color_brown,
                      worldsim.space_type_desert:    color_gray}

    def __init__(self, game_width=10, game_height=10):
        self.screen = None
        self.gm = worldsim.GameManager(width=game_width, height=game_height)

    @property
    def space_width(self):
        return self.screen.get_width() / self.gm.game_state.game_map.width

    @property
    def space_height(self):
        return self.screen.get_height() / self.gm.game_state.game_map.height

    def launch(self, width=500, height=500):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(Application.color_black)
        pygame.display.flip()

    def display_game(self):
        for space in self.gm.game_state.game_map.spaces:
            rect = self.get_space_rect(space)
            color = self.get_space_color(space)
            self.screen.fill(color, rect=rect)
        pygame.display.flip()

    def get_space_rect(self, space):
        left_x = space.x * self.space_width
        top_y = space.y * self.space_height
        return pygame.Rect(left_x, top_y, self.space_width, self.space_height)

    def get_space_color(self, space):
        return Application.terrain_colors[space.type]

    def close(self):
        pygame.display.quit()
