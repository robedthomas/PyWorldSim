import copy
import random
from abc import ABCMeta, abstractmethod


class GameManager(object):
    def __init__(self, game_state_file=None, width=0, height=0):
        if game_state_file:
            self.game_state = GameState(game_state_file=game_state_file)
        else:
            self.game_state = GameState(width=width, height=height)

    def exec_turn(self):
        next_turn = self.get_next_turn()
        self.game_state.turn_num += 1
        self.game_state.turn_history.append(next_turn)
        return next_turn.execute()

    def get_next_turn(self):
        return Turn(self.game_state)

    def save(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.game_state.to_save_string())


class GameComponent(metaclass=ABCMeta):
    def save(self, save_file):
        save_file.write(self.to_save_string() + "\n")

    @abstractmethod
    def to_save_string(self):
        raise NotImplementedError()

    @staticmethod
    def from_save_string(string):
        raise NotImplementedError()


class Turn(GameComponent):
    def __init__(self, game_state):
        self.game_state = game_state
        self.number = game_state.turn_num
        self.turn_steps = TurnStep.get_standard_steps()

    def execute(self):
        for turn_step in self.turn_steps:
            turn_step.execute(self.game_state)

    def to_save_string(self):
        save_string = "num:{}\nTurnSteps:".format(self.number)
        for step in self.turn_steps:
            save_string += "\n" + step.to_save_string()
        return save_string + "\n"


class TurnEvent(GameComponent, metaclass=ABCMeta):
    @abstractmethod
    def message(self):
        raise NotImplementedError()

    def to_save_string(self):
        return self.message


class ReproduceEvent(TurnEvent):
    def __init__(self, space, new_pop, from_random=False):
        self.space = space
        self.pop = new_pop
        self.random = from_random

    @property
    def message(self):
        msg = "New pop produced at ({},{})".format(self.space.x, self.space.y)
        if self.random:
            msg += " <RANDOM>"
        return msg


class MigrationEvent(TurnEvent):
    def __init__(self, pop, old_space, new_space):
        self.pop = pop
        self.old_space = old_space
        self.new_space = new_space

    @property
    def message(self):
        return "Pop migrated from ({},{}) to ({},{})".format(
            self.old_space.x, self.old_space.y,
            self.new_space.x, self.new_space.y
        )


class TurnStep(GameComponent, metaclass=ABCMeta):
    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)
        print(event.message)

    @staticmethod
    def get_standard_steps():
        return (ReproduceStep(), MigrateStep())

    @abstractmethod
    def execute(self, game_state):
        raise NotImplementedError()


class ReproduceStep(TurnStep):
    def execute(self, game_state):
        for space in game_state.game_map.spaces:
            space.populate(self)
        return self

    def to_save_string(self):
        if len(self.events) > 0:
            save_string = "ReproduceStep:"
            for event in self.events:
                save_string += "\n" + event.message
            return save_string
        return "ReproduceStep [empty]"


class MigrateStep(TurnStep):
    def execute(self, game_state):
        for space in game_state.game_map.spaces:
            space.migrate_pops(self)
        return self

    def to_save_string(self):
        if len(self.events) > 0:
            save_string = "MigrateStep:"
            for event in self.events:
                save_string += "\n" + event.message
            return save_string
        return "MigrateStep [empty]"


class GameState(GameComponent):
    def __init__(self, game_state_file=None, width=None, height=None):
        if game_state_file:
            with open(game_state_file) as f:
                self.from_save_string(f.read())
        else:
            self.game_map = GameMap.from_random(width, height)
            self.turn_num = 0
            self.turn_history = []

    def to_save_string(self):
        save_string = "Map:\n{}\n\nturn_num:{}\nTurns:\n".format(
            self.game_map.to_save_string(), self.turn_num)
        for turn in self.turn_history:
            save_string += turn.to_save_string()
        return save_string


class GameMap(GameComponent):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._space_arrays = []
        for x in range(width):
            self._space_arrays.append([])
            for y in range(height):
                self._space_arrays[x].append(None)

    @property
    def spaces(self):
        s = ()
        for column in self._space_arrays:
            for space in column:
                s += (space,)
        return s

    def add_space(self, new_space):
        self._space_arrays[new_space.x][new_space.y] = new_space

    def get_adjacent_spaces(self, space):
        adj = ()
        if (space.x > 0):
            adj += (self._space_arrays[space.x - 1][space.y],)
        if (space.x < self.width - 1):
            adj += (self._space_arrays[space.x + 1][space.y],)
        if (space.y > 0):
            adj += (self._space_arrays[space.x][space.y - 1],)
        if (space.y < self.height - 1):
            adj += (self._space_arrays[space.x][space.y + 1],)
        return adj

    @staticmethod
    def from_random(width, height):
        game_map = GameMap(width, height)
        space_types = (space_type_riverland, space_type_grassland,
                       space_type_dryland, space_type_hill,
                       space_type_mountain, space_type_desert)
        for x in range(width):
            for y in range(height):
                space_type = random.choice(space_types)
                game_map.add_space(Space(space_type, x, y, game_map))
        return game_map

    def to_save_string(self):
        save_string = "width:{}  height:{}\nSpaceTypes:".format(
            self.width, self.height)
        for space_type in (space_type_riverland,
                           space_type_grassland,
                           space_type_dryland,
                           space_type_hill,
                           space_type_mountain,
                           space_type_desert):
            save_string += "\n" + space_type.to_save_string()
        save_string += "\nSpaces:"
        for space in self.spaces:
            save_string += "\n" + space.to_save_string()
        return save_string


class SpaceType(GameComponent):
    _next_id = 0

    def __init__(self, type_name, food):
        self.name = type_name
        self.food = food
        self.id = SpaceType._next_id
        SpaceType._next_id += 1

    def to_save_string(self):
        return "id:{}  name:{}  food:{}".format(self.id, self.name, self.food)


space_type_riverland = SpaceType("Riverlands", 4)
space_type_grassland = SpaceType("Grasslands", 3)
space_type_dryland = SpaceType("Drylands", 2)
space_type_hill = SpaceType("Hills", 2)
space_type_mountain = SpaceType("Mountains", 1)
space_type_desert = SpaceType("Desert", 0)


class Space(GameComponent):
    max_growth = 5

    def __init__(self, space_type, x, y, game_map, growth=0):
        self.type = space_type
        self.x = copy.copy(x)
        self.y = copy.copy(y)
        self.game_map = game_map
        self.pops = []
        self.growth = growth

    @property
    def is_empty(self):
        return len(self.pops) == 0

    @property
    def num_pops(self):
        return len(self.pops)

    @property
    def food_consumed(self):
        return self.num_pops

    @property
    def surplus_food(self):
        return self.type.food - self.food_consumed

    def add_pop(self, pop):
        self.pops.append(pop)

    def remove_pop(self, pop):
        self.pops.remove(pop)

    def populate(self, reproduce_step):
        if self.num_pops >= 1:
            for pop in self.pops:
                pop.populate()
        else:
            self.empty_space_populate(reproduce_step)
        while self.growth >= Space.max_growth:
            new_pop = self.gen_pop()
            self.growth -= Space.max_growth
            reproduce_step.add_event(ReproduceEvent(self, new_pop))

    def empty_space_populate(self, reproduce_step):
        weight = 1
        adjacent_spaces = self.game_map.get_adjacent_spaces(self)
        for a in adjacent_spaces:
            if a.is_empty:
                weight += 1
        if weight > random.randrange(50):
            new_pop = self.gen_pop()
            reproduce_step.add_event(
                ReproduceEvent(self, new_pop, from_random=True))

    def get_pops_to_migrate(self):
        if self.surplus_food < 0:
            return self.pops
        return []

    def gen_pop(self):
        new_pop = Population(self)
        return new_pop

    def migrate_pops(self, migrate_step):
        migraters = self.get_pops_to_migrate()
        if len(migraters) > 0:
            adjacent_spaces = self.game_map.get_adjacent_spaces(self)
            space_to_move_to = random.choice(adjacent_spaces)
            pop_to_move = random.choice(migraters)
            pop_to_move.move(space_to_move_to)
            migrate_step.add_event(
                MigrationEvent(pop_to_move, self, space_to_move_to))

    def to_save_string(self):
        save_string = "type:{}  x:{}  y:{}  growth:{}\npops:".format(
            self.type.id, self.x, self.y, self.growth)
        for pop in self.pops:
            save_string += "\n" + pop.to_save_string()
        return save_string


class Population(GameComponent):
    def __init__(self, space):
        self.space = space
        self.space.add_pop(self)
        # self.culture = culture

    def change_culture(self, new_culture):
        self.culture = new_culture

    def move(self, new_space):
        self.space.remove_pop(self)
        self.space = new_space
        self.space.add_pop(self)

    def populate(self):
        self.space.growth += 1

    def to_save_string(self):
        return "{} {}".format(self.space.x, self.space.y)
