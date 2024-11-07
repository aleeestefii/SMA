from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

class CleaningRobot(Agent):
    def __init__(self, id, simulation):
        super().__init__(id, simulation)

    def random_move(self):
        """Moves the agent to a random adjacent cell."""
        adjacent_cells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        next_position = self.random.choice(adjacent_cells)
        self.model.grid.move_agent(self, next_position)

    def step(self):
        #it checsk if the current cell is dirty and clean it if needed
        current_cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in current_cell_contents:
            if isinstance(obj, GridTile) and obj.status == 1:
                obj.status = 0
                return
        #anoteher cell if clean
        self.random_move()

class GridTile(Agent):
    """Represents a tile in the grid that can be clean or dirty."""
    def __init__(self, id, simulation, status):
        super().__init__(id, simulation)
        self.status = status

class CleaningSimulation(Model):
    def __init__(self, robot_count, grid_width, grid_height, steps_remaining, dirt_percentage):
        super().__init__()
        self.steps_remaining = steps_remaining
        self.grid = MultiGrid(grid_width, grid_height, False)
        self.schedule = RandomActivation(self)

        #number of dirty cells 
        total_tiles = grid_width * grid_height
        dirty_tiles = int(total_tiles * dirt_percentage)
        dirty_positions = random.sample(
            [(x, y) for x in range(grid_width) for y in range(grid_height)], dirty_tiles
        )

        for x in range(grid_width):
            for y in range(grid_height):
                tile_status = 1 if (x, y) in dirty_positions else 0
                tile = GridTile((x, y), self, tile_status)
                self.grid.place_agent(tile, (x, y))


        initial_position = (1, 1)
        for i in range(robot_count):
            robot = CleaningRobot(i, self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, initial_position)

    def step(self):
        """Advance the model by one step."""
        if self.steps_remaining <= 0:
            print("Simulation ended")
            self.running = False
        else:
            self.schedule.step()
            self.steps_remaining -= 1

def render_agent(agent):
    if isinstance(agent, CleaningRobot):
        return {
            "Shape": "circle",
            "Color": "pink",  #robot
            "Filled": True,
            "Layer": 1,
            "r": 0.5
        }
    elif isinstance(agent, GridTile):
        color = "#b2ac88" if agent.status == 1 else "white"  #dirt
        return {
            "Shape": "rect",
            "Color": color,
            "Filled": True,
            "Layer": 0,
            "w": 1,
            "h": 1
        }