from abc import ABCMeta, abstractmethod
from pyworldsim import worldsim
import pygame


color_black = pygame.Color(0, 0, 0)
color_gray = pygame.Color(183, 194, 255)
color_brown = pygame.Color(127, 51, 0)
color_blue = pygame.Color(38, 88, 255)
color_green = pygame.Color(83, 124, 0)
color_yellow = pygame.Color(255, 229, 0)
color_orange = pygame.Color(255, 148, 0)
color_red = pygame.Color(255, 42, 0)


class Application(object):
    def __init__(self, game_width=10, game_height=10):
        self.screen = None
        self.gm = worldsim.GameManager(width=game_width, height=game_height)
        self.gui_state = GuiGameState(self.gm.game_state)

    def launch(self, width=500, height=500):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(color_black)
        pygame.display.flip()

    def pass_turn(self, num=1):
        for i in range(num):
            self.gm.exec_turn()

    def display_game(self):
        self.screen.fill(color_black)
        self.gui_state.draw(self.screen)
        pygame.display.flip()

    def close(self):
        pygame.display.quit()


class GuiComponent(object, metaclass=ABCMeta):
    @abstractmethod
    def draw(self, surface):
        raise NotImplementedError()


class GuiGameState(GuiComponent):
    def __init__(self, src_state):
        self.src_state = src_state
        self.gui_map = GuiMap(self.src_state.game_map)

    def get_map_width(self, surface):
        return surface.get_width()

    def get_map_height(self, surface):
        return surface.get_height()

    def get_map_rect(self, surface):
        width = self.get_map_width(surface)
        height = self.get_map_height(surface)
        return pygame.Rect(0, 0, width, height)

    def get_map_surface(self, surface):
        return surface.subsurface(self.get_map_rect(surface))

    def draw(self, surface):
        self.gui_map.draw(self.get_map_surface(surface))


class GuiMap(GuiComponent):
    def __init__(self, src_map):
        self.src_map = src_map
        self.gui_spaces = []
        for space in self.src_map.spaces:
            self.gui_spaces.append(GuiSpace(space))

    def get_space_width(self, gui_space, surface):
        return surface.get_width() / self.src_map.width

    def get_space_height(self, gui_space, surface):
        return surface.get_height() / self.src_map.height

    def get_space_rect(self, gui_space, surface):
        width = self.get_space_width(gui_space, surface)
        height = self.get_space_height(gui_space, surface)
        left_x = gui_space.src_space.x * width
        top_y = gui_space.src_space.y * height
        return pygame.Rect(left_x, top_y, width, height)

    def get_space_surface(self, gui_space, surface):
        return surface.subsurface(self.get_space_rect(gui_space, surface))

    def draw(self, surface):
        for gui_space in self.gui_spaces:
            gui_space.draw(self.get_space_surface(gui_space, surface))


class GuiSpace(GuiComponent):
    terrain_colors = {worldsim.space_type_riverland: color_green,
                      worldsim.space_type_grassland: color_yellow,
                      worldsim.space_type_dryland:   color_orange,
                      worldsim.space_type_hill:      color_red,
                      worldsim.space_type_mountain:  color_brown,
                      worldsim.space_type_desert:    color_gray}

    def __init__(self, src_space):
        self.src_space = src_space

    @property
    def color(self):
        return GuiSpace.terrain_colors[self.src_space.type]

    @property
    def gui_pops(self):
        for pop in self.src_space.pops:
            yield GuiPop(pop)

    def get_pop_rows(self, surface):
        return 3

    def get_pop_columns(self, surface):
        return 3

    def get_pop_margin(self, gui_pop, surface):
        return 2

    def get_pop_width(self, gui_pop, surface):
        margin = self.get_pop_margin(gui_pop, surface)
        columns = self.get_pop_columns(surface)
        return (surface.get_width() - (columns + 1) * margin) // columns

    def get_pop_height(self, gui_pop, surface):
        margin = self.get_pop_margin(gui_pop, surface)
        rows = self.get_pop_rows(surface)
        return (surface.get_height() - (rows + 1) * margin) // rows

    def get_pop_index(self, gui_pop):
        return self.src_space.pops.index(gui_pop.src_pop)

    def get_pop_row(self, gui_pop, surface):
        return self.get_pop_index(gui_pop) // self.get_pop_columns(surface)

    def get_pop_column(self, gui_pop, surface):
        return self.get_pop_index(gui_pop) % self.get_pop_columns(surface)

    def get_pop_rect(self, gui_pop, surface):
        pop_row = self.get_pop_row(gui_pop, surface)
        pop_column = self.get_pop_column(gui_pop, surface)
        pop_width = self.get_pop_width(gui_pop, surface)
        pop_height = self.get_pop_height(gui_pop, surface)
        margin = self.get_pop_margin(gui_pop, surface)
        x_offset = (pop_column + 1) * margin + (pop_column * pop_width)
        y_offset = (pop_row + 1) * margin + (pop_row * pop_height)
        return pygame.Rect(x_offset, y_offset, pop_width, pop_height)

    def get_pop_surface(self, gui_pop, surface):
        return surface.subsurface(self.get_pop_rect(gui_pop, surface))

    def draw(self, surface):
        surface.fill(self.color)
        for gui_pop in self.gui_pops:
            gui_pop.draw(self.get_pop_surface(gui_pop, surface))


class GuiPop(GuiComponent):
    def __init__(self, src_pop):
        self.src_pop = src_pop

    @property
    def color(self):
        return color_black

    def draw(self, surface):
        surface.fill(self.color)


class GuiHelpers(object):
    @staticmethod
    def relative_coordinates(container_rect, x_offset, y_offset):
        return (container_rect.left + x_offset, container_rect.top + y_offset)

    def fractional_coordinates(container_rect, x_fraction, y_fraction):
        return (container_rect.left + (container_rect.width * x_fraction),
                container_rect.top + (container_rect.height * y_fraction))
