"""
Simulación de robots de limpieza utilizando el framework Mesa.
Este programa simula el comportamiento de robots que limpian una habitación.

Alejandra Estefanía Rico González A01749850
Carlos Alberto Zamudio Velazquez A01799283
Fecha de creación: 4 de Noviembre de 2024
Última modificación: 6 de Noviembre de 2024
"""

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider
from mesa.visualization.modules import CanvasGrid
import random
import time

class CleaningRobot(Agent):
    """
    Robot de limpieza que se mueve por la cuadrícula y limpia celdas sucias.
    
    Atributos:
        cellsCleaned (int): Contador de celdas limpiadas por este robot
        totalMovements (int): Contador de movimientos realizados
    """
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cellsCleaned = 0
        self.totalMovements = 0
        
    def randomMove(self):
        """
        Mueve el robot a una celda adyacente aleatoria válida.
        
        El movimiento se realiza considerando las 8 celdas adyacentes (moore=True),
        verificando que estén dentro de los límites de la cuadrícula.
        """
        adjacentCells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        # Filtrar celdas fuera de los límites
        validCells = [cell for cell in adjacentCells 
                      if 0 <= cell[0] < self.model.grid.width 
                      and 0 <= cell[1] < self.model.grid.height]
        
        if validCells:
            nextPosition = self.random.choice(validCells)
            self.model.grid.move_agent(self, nextPosition)
            self.totalMovements += 1

    def step(self):
        """
        Ejecuta un paso de la simulación para el robot.
        
        Si la celda actual está sucia, la limpia e incrementa los contadores.
        Si la celda está limpia, se mueve a una posición adyacente.
        """
        # Verificar si la celda actual está sucia y limpiarla si es necesario
        currentCellContents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in currentCellContents:
            if isinstance(obj, GridTile) and obj.status == 1:
                obj.status = 0
                self.cellsCleaned += 1
                self.model.cleanCells += 1
                return
        # Moverse a otra celda si está limpia
        self.randomMove()

class GridTile(Agent):
    """
    Representa una celda en la cuadrícula.
    
    Atributos:
        status (int): Estado de la celda (0: limpia, 1: sucia)
    """
    
    def __init__(self, unique_id, model, status):
        super().__init__(unique_id, model)
        self.status = status

class CleaningSimulation(Model):
    """
    Modelo principal que controla la simulación de limpieza.
    
    Parámetros:
        width (int): Ancho de la cuadrícula
        height (int): Alto de la cuadrícula
        robotCount (int): Número de robots de limpieza
        dirtPercentage (float): Porcentaje de celdas sucias al inicio
        maxTime (int): Tiempo máximo de simulación en segundos
    """
    
    def __init__(self, width, height, robotCount, dirtPercentage, maxTime):
        super().__init__()
        self.running = True
        self.robotCount = robotCount
        self.gridWidth = width
        self.gridHeight = height
        self.maxTime = maxTime  # Tiempo máximo en segundos
        self.startTime = time.time()  # Tiempo de inicio de la simulación
        self.dirtPercentage = dirtPercentage
        
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        
        # Estadísticas
        self.cleanCells = 0
        self.initialDirtyCells = int(width * height * dirtPercentage)
        self.stepsExecuted = 0
        
        self.setupEnvironment()
        
    def setupEnvironment(self):
        """
        Configura el estado inicial del entorno.
        
        Distribuye aleatoriamente las celdas sucias según el porcentaje especificado
        y coloca los robots en su posición inicial (1,1).
        """
        # Colocar celdas sucias
        dirtyPositions = random.sample(
            [(x, y) for x in range(self.gridWidth) for y in range(self.gridHeight)],
            self.initialDirtyCells
        )
        
        # Crear todas las celdas
        for x in range(self.gridWidth):
            for y in range(self.gridHeight):
                tileStatus = 1 if (x, y) in dirtyPositions else 0
                tile = GridTile(f"tile_{x}_{y}", self, tileStatus)
                self.grid.place_agent(tile, (x, y))
        
        # Colocar robots
        initialPosition = (1, 1)
        for i in range(self.robotCount):
            robot = CleaningRobot(f"robot_{i}", self)
            self.schedule.add(robot)
            self.grid.place_agent(robot, initialPosition)
    
    def getStatistics(self):
        """
        Recopila y retorna las estadísticas actuales de la simulación.
        
        Returns:
            dict: Diccionario con porcentaje completado, tiempo transcurrido 
                 y movimientos totales de los robots
        """
        robots = [agent for agent in self.schedule.agents if isinstance(agent, CleaningRobot)]
        elapsedTime = time.time() - self.startTime
        stats = {
            "PorcentajeCompletado": (self.cleanCells / self.initialDirtyCells) * 100,
            "TiempoTranscurrido": elapsedTime,
            "MovimientosTotales": sum(robot.totalMovements for robot in robots)
        }
        return stats

    def step(self):
        """Avanza la simulación un paso."""
        elapsedTime = time.time() - self.startTime
        
        if elapsedTime >= self.maxTime or self.cleanCells >= self.initialDirtyCells:
            self.running = False
            print("\nSimulación finalizada")
            print("\nEstadísticas finales:")
            stats = self.getStatistics()
            for key, value in stats.items():
                if key in ["TiempoTranscurrido", "PorcentajeCompletado"]:
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
        else:
            self.schedule.step()
            self.stepsExecuted += 1

def renderAgent(agent):
    """
    Define la representación visual de los agentes en la interfaz gráfica.
    
    Args:
        agent: Instancia de CleaningRobot o GridTile
        
    Returns:
        dict: Configuración visual del agente (forma, color, tamaño)
    """
    if isinstance(agent, CleaningRobot):
        return {
            "Shape": "circle",
            "Color": "red",  # Robot
            "Filled": True,
            "Layer": 1,
            "r": 0.8,
            "text": f"R{agent.unique_id[-1]}",
            "text_color": "white"
        }
    elif isinstance(agent, GridTile):
        colors = {0: "white", 1: "#665c54"}
        return {
            "Shape": "rect",
            "Color": colors[agent.status],
            "Filled": True,
            "Layer": 0,
            "w": 0.9,
            "h": 0.9
        }

def createSimulationServer():
    """
    Configura y crea el servidor de visualización web.
    
    Returns:
        ModularServer: Servidor configurado con los parámetros y visualización
    """
    
    # Definir los parámetros que el usuario puede configurar
    modelParams = {
        "width": Slider(
            "Ancho de la habitación",
            value = 10,
            min_value = 5,
            max_value = 20,
            step = 1,
            description="Ancho de la cuadrícula (M)"
        ),
        "height": Slider(
            "Alto de la habitación",
            value = 10,
            min_value = 5,
            max_value = 20,
            step = 1,
            description="Alto de la cuadrícula (N)"
        ),
        "robotCount": Slider(
            "Número de robots",
            value = 1,
            min_value = 1,
            max_value = 10,
            step = 1,
            description="Cantidad de robots de limpieza"
        ),
        "dirtPercentage": Slider(
            "Porcentaje de suciedad",
            value = 0.3,
            min_value = 0.1,
            max_value = 0.9,
            step = 0.1,
            description="Porcentaje de celdas inicialmente sucias"
        ),
        "maxTime": Slider(
            "Tiempo máximo (segundos)",
            value = 60,
            min_value = 10,
            max_value = 300,
            step = 10,
            description="Tiempo máximo de ejecución en segundos"
        )
    }

    # Crear visualización de la cuadrícula
    grid = CanvasGrid(renderAgent, 20, 20, 500, 500)
    
    # Crear y retornar el servidor
    server = ModularServer(
        CleaningSimulation,
        [grid],
        "Simulación de Robots de Limpieza",
        modelParams
    )
    return server

if __name__ == "__main__":
    server = createSimulationServer()
    server.port = 8521
    server.launch()