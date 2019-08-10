from abc import ABCMeta, abstractmethod
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
        self.spaces = []
        for space in self.gm.game_state.game_map.spaces:
            self.spaces.append(GuiSpace(space, self))

    @property
    def pops(self):
        return self.gm.game_state.game_map.pops

    @property
    def space_width(self):
        return self.screen.get_width() / self.gm.game_state.game_map.width

    @property
    def space_height(self):
        return self.screen.get_height() / self.gm.game_state.game_map.height

    @property
    def pop_width(self):
        return (self.space_width - (self.pop_columns + 1) * self.pop_margin) / self.pop_columns

    @property
    def pop_height(self):
        return (self.space_height - (self.pop_rows + 1) * self.pop_margin) / self.pop_rows

    @property
    def pop_margin(self):
        return 2

    @property
    def pop_rows(self):
        return 3

    @property
    def pop_columns(self):
        return 3

    def launch(self, width=500, height=500):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(Application.color_black)
        pygame.display.flip()

    def pass_turn(self, num=1):
        for i in range(num):
            self.gm.exec_turn()

    def display_game(self):
        self.screen.fill(Application.color_black)
        self.draw_spaces()
        self.draw_pops()
        pygame.display.flip()

    def draw_spaces(self):
        for space in self.spaces:
            space.draw()

    def draw_pops(self):
        for space in self.spaces:
            space.draw_pops()

    def close(self):
        pygame.display.quit()


class GuiComponent(object, metaclass=ABCMeta):
    @abstractmethod
    def get_rect(self):
        raise NotImplementedError()

    @abstractmethod
    def draw(self):
        raise NotImplementedError()


class GuiSpace(GuiComponent):
    def __init__(self, src_space, parent_app):
        self.src_space = src_space
        self.parent_app = parent_app

    def get_rect(self):
        left_x = self.src_space.x * self.parent_app.space_width
        top_y = self.src_space.y * self.parent_app.space_height
        return pygame.Rect(left_x, top_y, self.parent_app.space_width,
                           self.parent_app.space_height)

    def get_color(self):
        return Application.terrain_colors[self.src_space.type]

    def draw(self):
        self.parent_app.screen.fill(self.get_color(), rect=self.get_rect())

    def draw_pops(self):
        for pop in self.src_space.pops:
            gui_pop = GuiPop(pop, self, self.parent_app)
            gui_pop.draw()


class GuiPop(GuiComponent):
    def __init__(self, src_pop, parent_space, parent_app):
        self.src_pop = src_pop
        self.parent_space = parent_space
        self.parent_app = parent_app

    @property
    def index(self):
        return self.parent_space.src_space.pops.index(self.src_pop)

    @property
    def row(self):
        return self.index // self.parent_app.pop_columns

    @property
    def column(self):
        return self.index % self.parent_app.pop_columns

    def get_rect(self):
        x_offset = (self.column + 1) * self.parent_app.pop_margin + (
            self.column * self.parent_app.pop_width)
        y_offset = (self.row + 1) * self.parent_app.pop_margin + (
            self.row * self.parent_app.pop_height)
        space_rect = self.parent_space.get_rect()
        left_x, top_y = GuiHelpers.relative_coordinates(space_rect, x_offset, y_offset)
        return pygame.Rect(left_x, top_y, self.parent_app.pop_width,
                           self.parent_app.pop_height)

    def get_color(self):
        return Application.color_black

    def draw(self):
        self.parent_app.screen.fill(self.get_color(), rect=self.get_rect())


class GuiHelpers(object):
    @staticmethod
    def relative_coordinates(container_rect, x_offset, y_offset):
        return (container_rect.left + x_offset, container_rect.top + y_offset)

    def fractional_coordinates(container_rect, x_fraction, y_fraction):
        return (container_rect.left + (container_rect.width * x_fraction),
                container_rect.top + (container_rect.height * y_fraction))
