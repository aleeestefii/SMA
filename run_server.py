from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from cleaning_robot import CleaningSimulation, render_agent


grid_width = 10  
grid_height = 10
canvas_element = CanvasGrid(render_agent, grid_width, grid_height, 500, 500)

robot_count = 5
steps_remaining = 100
dirt_percentage = 0.3

server = ModularServer(
    CleaningSimulation,
    [canvas_element],
    "Cleaning Simulation",
    {"robot_count": robot_count, "grid_width": grid_width, "grid_height": grid_height,
     "steps_remaining": steps_remaining, "dirt_percentage": dirt_percentage},
)

server.port = 8521 
server.launch()