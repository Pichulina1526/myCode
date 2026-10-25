# settings.py

TILE_SIZE = 38
ARENA_BOUND_X = 1280
ARENA_BOUND_Y = 960
FPS = 60



def load_map(filepath):
    grid= []
    with open(filepath,"r") as file:
        for line in file:
            row = [int(cell) for cell in line.strip().split(",")]
            grid.append(row)
    return grid


GRID_MAP = load_map("map.csv")