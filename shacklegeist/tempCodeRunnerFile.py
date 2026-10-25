import pygame
import sys
from settings import TILE_SIZE, GRID_MAP, ARENA_BOUND_X, ARENA_BOUND_Y


# pathfinder/ render grid
class Tile:
    def __init__(self, col_index, row_index, tile_type):
        self.col = col_index
        self.row = row_index
        self.position = pygame.math.Vector2(col_index * TILE_SIZE, row_index * TILE_SIZE)
        self.tile_type = tile_type

        # Pathfinding parameters pre-allocated for later milestones
        self.cost = float("inf")
        self.visited = False
        self.flow_direction = pygame.math.Vector2(0, 0)

        # Default environment properties  
        self.colour = (34, 139, 34)
        self.is_obstacle = False
        self.speed_modifier = 1.0
        self.disables_actions = False
        self.is_hazard = False

        # Determine even tiles for procedural checkered pattern  
        is_even_tile = (self.col + self.row) % 2 == 0

        # Setting tile visual and mechanical types  
        if self.tile_type == 0:
            self.colour = (50, 205, 52) if is_even_tile else (45, 195, 45)
        elif self.tile_type == 1:
            self.speed_modifier = 0.85
            self.colour = (0, 100, 0) if is_even_tile else (0, 90, 0)
        elif self.tile_type == 2:
            self.speed_modifier = 0.4
            self.disables_actions = True
            self.colour = (0, 100, 255) if is_even_tile else (30, 90, 250)
        elif self.tile_type == 3:
            self.is_hazard = True
            self.colour = (230, 50, 50) if is_even_tile else (210, 40, 40)
        elif self.tile_type == 4:
            self.is_obstacle = True
            self.colour = (105, 105, 105) if is_even_tile else (128, 128, 128)

    def draw(self, rendering_surface, viewport_offset_vector):
        render_pos_x = self.position.x - viewport_offset_vector.x
        render_pos_y = self.position.y - viewport_offset_vector.y
        pygame.draw.rect(rendering_surface, self.colour, (render_pos_x, render_pos_y, TILE_SIZE, TILE_SIZE))


class SpatialMappingSandbox:
    def __init__(self):
        pygame.init()
        self.diagnostic_canvas = pygame.display.set_mode((ARENA_BOUND_X, ARENA_BOUND_Y))
        pygame.display.set_caption("Milestone 1: Isolated Environment Renderer")
        self.frame_synchronizer = pygame.time.Clock()

        # Static camera offset locked to top-left for base map testing
        self.static_viewport_anchor = pygame.math.Vector2(0, 0)

        # Instantiate the OOP terrain grid
        self.terrain_object_matrix = self.assemble_terrain_matrix()

    def assemble_terrain_matrix(self):
        constructed_layout = []
        for y_coordinate, row_data in enumerate(GRID_MAP):
            constructed_row = []
            for x_coordinate, numeric_tile_id in enumerate(row_data):
                constructed_row.append(Tile(x_coordinate, y_coordinate, numeric_tile_id))
            constructed_layout.append(constructed_row)
        return constructed_layout

    def execute_diagnostic_loop(self):
        sandbox_active = True
        while sandbox_active:
            for intercepted_event in pygame.event.get():
                if intercepted_event.type == pygame.QUIT:
                    sandbox_active = False
                    pygame.quit()
                    sys.exit()

            self.diagnostic_canvas.fill((30, 30, 30))

            # Adapted view frustum culling for static testing
            cull_limit_col = min(len(self.terrain_object_matrix[0]), (ARENA_BOUND_X // TILE_SIZE) + 2)
            cull_limit_row = min(len(self.terrain_object_matrix), (ARENA_BOUND_Y // TILE_SIZE) + 2)

            for row_idx in range(0, cull_limit_row):
                for col_idx in range(0, cull_limit_col):
                    visual_tile = self.terrain_object_matrix[row_idx][col_idx]
                    visual_tile.draw(self.diagnostic_canvas, self.static_viewport_anchor)

            pygame.display.flip()
            self.frame_synchronizer.tick(60)


if __name__ == "__main__":
    milestone_one_tester = SpatialMappingSandbox()
    milestone_one_tester.execute_diagnostic_loop()