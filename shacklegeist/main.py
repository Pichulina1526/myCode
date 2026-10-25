# main.py
import pygame
import sys
from enum import Enum
from settings import *
import random
import heapq
import math

## turn off enemy collisions with wall for firs 3 secs

pygame.font.init()

# Enums
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    BOSS = 3
    GAMEOVER = 4

# pathfinder/render grid
class Tile:
    def __init__(self, col_index,row_index, tile_type):
        self.col = col_index
        self.row = row_index
        self.position = pygame.math.Vector2(col_index * TILE_SIZE,row_index * TILE_SIZE)
        self.tile_type = tile_type

        # pathfinding variables for future pathfinding algorithm:
        self.cost = float("inf")
        self.visited = False
        self.flow_direction = pygame.math.Vector2(0,0)

        #default properties for each tile
        self.colour = (34,139,34)
        self.is_obstacle = False
        self.speed_modifier = 1.0
        self.disables_actions = False
        self.is_hazard = False

        #determine even tiles for checkered patter
        is_even_tile = (self.col + self.row) % 2 == 0


        #setting tile types for different numbers in grid
        if self.tile_type == 0:# light grass - walkable
            if is_even_tile:
                self.colour = (50,205,52)
            else:
                self.colour = (45,195,45)

        if self.tile_type == 1: #dark tall grass - walkable but slow
            self.speed_modifier = 0.85
            if is_even_tile:
                self.colour = (0,100,0)
            else:
                self.colour = (0,90,0)

        elif self.tile_type == 2: #water - walkable very slow and no actions
            self.speed_modifier = 0.4
            self.disables_actions = True
            if is_even_tile:
                self.colour = (0,100,255)
            else:
                self.colour = (30,90,250)

        elif self.tile_type == 3: #lava - walkable hazard, damage dealing
            self.is_hazard = True
            if is_even_tile:
                self.colour = (230,50,50)
            else:
                self.colour = (210,40,40)

        elif self.tile_type == 4: # grey cobblestone - impermeable
            self.is_obstacle = True
            if is_even_tile:
                self.colour = (105,105,105)
            else:
                self.colour = (128,128,128)
                           

    def draw(self,surface, camera_offset):
        draw_x = self.position.x - camera_offset.x
        draw_y = self.position.y - camera_offset.y

        pygame.draw.rect(surface,self.colour, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))


class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2(0,0)
        self.shake_end_time = 0
        self.shake_intensity = 0

    def start_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_end_time = pygame.time.get_ticks() + duration


    def update(self, target, map_cols, map_rows):

        ideal_x = target.rect.centerx - (ARENA_BOUND_X // 2)
        ideal_y = target.rect.centery - (ARENA_BOUND_Y // 2)

        max_scroll_x = (map_cols * TILE_SIZE) - ARENA_BOUND_X
        max_scroll_y = (map_rows * TILE_SIZE) - ARENA_BOUND_Y

        max_scroll_x = max(0, max_scroll_x)
        max_scroll_y = max(0, max_scroll_y)

        self.offset.x = max(0, min(ideal_x, max_scroll_x))
        self.offset.y = max(0, min(ideal_y, max_scroll_y))

        current_time = pygame.time.get_ticks()
        if current_time < self.shake_end_time:
            self.offset.x += random.randint(-self.shake_intensity, self.shake_intensity)
            self.offset.y += random.randint(-self.shake_intensity, self.shake_intensity)

class Pathfinder:
    def __init__(self, map_cols, map_rows):
        self.map_cols = map_cols
        self.map_rows = map_rows

        self.cost_field = [[float("inf")for _ in range(map_cols)] for _ in range(map_rows)]
        self.flow_field = [[pygame.math.Vector2(0,0) for _ in range(map_cols)] for _ in range (map_rows)]

        #dirty flag
        self.last_target_col = -1
        self.last_target_row = -1

        self.last_update_time = 0
        self.update_cooldown = 100

        ## track old search window
        self.last_window = (0,0,0,0)

    def generate_flow_field(self,grid,target_rect):
        target_col = int(target_rect.centerx // TILE_SIZE)
        target_row = int(target_rect.centery // TILE_SIZE)


        #state cache
        if target_col == self.last_target_col and target_row == self.last_target_row:
            return

        #time throttling
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time < self.update_cooldown:
            return

        self.last_update_time = current_time
        self.last_target_col = target_col
        self.last_target_row = target_row

        #spatial window
        search_radius = 35
        start_col = max(0, target_col - search_radius)
        end_col = min(self.map_cols, target_col + search_radius)
        start_row = max(0, target_row - search_radius)
        end_row = min(self.map_rows, target_row + search_radius)

        #elliminate ghost vectors
        old_start_c, old_end_c, old_start_r, old_end_r = self.last_window
        for r in range(old_start_r, old_end_r):
            for c in range(old_start_c, old_end_c):
                self.cost_field[r][c] = float("inf")
                self.flow_field[r][c] = pygame.math.Vector2(0,0)

        self.last_window = (start_col, end_col, start_row, end_row)

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                self.cost_field[r][c] = float("inf")
                self.flow_field[r][c] = pygame.math.Vector2(0,0)



        self.cost_field[target_row][target_col] = 0

        queue = []
        heapq.heappush(queue, (0, target_col, target_row))

        directions = [(0,-1), (0,1), (-1,0), (1,0)]


        #phase 1 - local djikstrra
        while len(queue) > 0:
            current_cost, current_col, current_row = heapq.heappop(queue)

            #skip if there is a cheaper route to plkayer
            if current_cost > self.cost_field[current_row][current_col]:
                continue

            for d_col, d_row in directions:
                n_col = current_col + d_col
                n_row = current_row + d_row

                if start_col <= n_col < end_col and start_row <= n_row < end_row:
                    target_tile = grid[n_row][n_col]

                    #1. skip barriers
                    if target_tile.is_obstacle or target_tile.is_hazard:
                        continue

                    #2. invisible buffer
                    proximity_penalty = 0
                    for check_d_col, check_d_row in directions:
                        adj_col = n_col + check_d_col
                        adj_row = n_row + check_d_row
                        if start_col <= adj_col < end_col and start_row <= adj_row < end_row:
                            if grid[adj_row][adj_col].is_obstacle:
                                proximity_penalty = 5
                                break

                    #3. dynamic terrain cost
                    terrain_cost = 1.0 / getattr(target_tile, "speed_modifier", 1.0)

                    #4. calc traversal cost
                    new_cost = current_cost + terrain_cost + proximity_penalty

                    if new_cost < self.cost_field[n_row][n_col]:
                        self.cost_field[n_row][n_col] = new_cost
                        heapq.heappush(queue, (new_cost, n_col, n_row))


        # phase 2 - vector generation
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if grid[row][col].is_obstacle:
                    continue

                min_cost = self.cost_field[row][col]
                best_dir = pygame.math.Vector2(0,0)

                ## checking 8 neighbours to find best direction
                for d_col, d_row in [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]:
                    n_col = col + d_col
                    n_row = row + d_row

                    if start_col <= n_col < end_col and start_row <= n_row < end_row:
                        if self.cost_field[n_row][n_col] < min_cost:
                            min_cost = self.cost_field[n_row][n_col]
                            best_dir = pygame.math.Vector2(d_col,d_row)

                if best_dir.length() > 0:
                    self.flow_field[row][col] = best_dir.normalize()


class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.is_attacking = False
        self.attack_start_time = 0
        self.last_attack_time = 0

        self.hit_wallx = False
        self.current_tip_x = 0
        self.current_tip_y = 0

        #base variables for child  classes
        self.weapon_name = "base"
        self.damage = 0
        self.cooldown = 0
        self.attack_duration = 0
        self.knockback_force = 0


    def attack(self, target_pos):
        pass

    def update(self, enemies, chests = None, grid = None):
        pass

    def draw(self, surface, camera_offset):
        pass


class Sword(Weapon):
    def __init__(self, owner):
        super().__init__(owner)
        self.weapon_name = "Sword"
        self.damage = 40
        self.cooldown = 350
        self.attack_duration = 480
        self.range = TILE_SIZE * 2.5
        self.knockback_force = 18

        ## swing arc variables
        self.swing_angle_span = math.radians(270)
        self.base_angle = 0
        self.current_angle = 0
        self.enemies_hit = set()

    def attack(self, target_pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.cooldown:
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            self.enemies_hit.clear()
            self.hit_wallx = False

            ## calculating base vector
            dx = target_pos[0] - self.owner.rect.centerx
            dy = target_pos[1] - self.owner.rect.centery
            self.base_angle = math.atan2(dy, dx)


    def update(self, enemies, chests = None, grid = None):
        if not self.is_attacking:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.attack_start_time

        ## stop swing if duration exceeded
        if elapsed > self.attack_duration:
            self.is_attacking = False


        ## lerp angle
        progress = elapsed / self.attack_duration
        start_angle = self.base_angle - (self.swing_angle_span / 2)
        end_angle = self.base_angle + (self.swing_angle_span / 2)
        self.current_angle = start_angle + (end_angle - start_angle) * progress

        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        tip_x = cx + math.cos(self.current_angle) * self.range
        tip_y = cy + math.sin(self.current_angle) * self.range

        hit_dir = pygame.math.Vector2(math.cos(self.base_angle), math.sin(self.base_angle))

        #wall collision
        closest_dist = self.range
        hit_wall = False
        if grid:
            start_c = max(0, int((cx - self.range)// TILE_SIZE))
            end_c = min(len(grid[0]) - 1, int((cx + self.range) // TILE_SIZE))
            start_r = max (0, int((cy - self.range) // TILE_SIZE))
            end_r = min(len(grid) - 1, int((cy + self.range) // TILE_SIZE))

            for row in range(start_r, end_r + 1):
                for col in range(start_c, end_c + 1):
                    tile = grid[row][col]
                    if tile.is_obstacle:
                        tile_rect = pygame.Rect(tile.position.x, tile.position.y, TILE_SIZE, TILE_SIZE)
                        clip = tile_rect.clipline((cx, cy) , (tip_x,tip_y))
                        if clip:
                            dist = math.hypot(clip[0][0] - cx, clip[0][1] - cy)
                            if dist < closest_dist:
                                closest_dist = dist
                                hit_wall = True

        if hit_wall:
            tip_x = cx + math.cos(self.current_angle) * closest_dist
            tip_y = cy + math.sin(self.current_angle) * closest_dist
            if not getattr(self, "hit_wallx", False):
                self.owner.apply_knockback(-hit_dir, self.knockback_force * 0.5)
                self.owner.shake_req = (4,150)
                self.hit_wallx = True

        self.current_tip_x = tip_x
        self.current_tip_y = tip_y


        for enemy in enemies:
            if enemy not in self.enemies_hit and not enemy.is_dead:
                if enemy.rect.clipline((cx, cy), (tip_x, tip_y)):
                    enemy.take_damage(self.damage, hit_dir, self.knockback_force, self.weapon_name)
                    self.owner.apply_knockback(-hit_dir, self.knockback_force * 0.3)
                    self.enemies_hit.add(enemy)
                    if enemy.is_dead:
                        self.owner.shake_req = (8, 200)
                    else:
                        if not self.owner.shake_req or self.owner.shake_req[0] < 8:
                            self.owner.shake_req = (4,100)


        if chests:
            for chest in chests:
                if chest not in self.enemies_hit and not chest.is_broken:
                    if chest.rect.clipline((cx, cy), (tip_x, tip_y)):
                        chest.break_open()
                        self.enemies_hit.add(chest)



    def draw(self, surface, camera_offset):
        if not self.is_attacking:
            return

        cx = self.owner.rect.centerx - camera_offset.x
        cy = self.owner.rect.centery - camera_offset.y

        tip_x = cx + math.cos(self.current_angle) * self.range
        tip_y = cy + math.sin(self.current_angle) * self.range

        pygame.draw.line(surface, (220,220,220), (cx, cy), (tip_x, tip_y), 10)




class Spear(Weapon):
    def __init__(self, owner):
        super().__init__(owner)
        self.weapon_name = "Spear"
        self.damage = 10
        self.cooldown = 350
        self.attack_duration = 220
        self.range = TILE_SIZE * 6
        self.knockback_force = 45

        self.base_angle = 0
        self.current_dist = 0
        self.enemies_hit = set()

    def attack(self, target_pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.cooldown:
            self.is_attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            self.enemies_hit.clear()
            self.hit_wallx = False

            dx = target_pos[0] - self.owner.rect.centerx
            dy = target_pos[1] - self.owner.rect.centery
            self.base_angle = math.atan2(dy, dx)

    def update(self, enemies, chests = None, grid = None):
        if not self.is_attacking: return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.attack_start_time

        if elapsed > self.attack_duration:
            self.is_attacking = False
            return

        progress = elapsed / self.attack_duration

        if progress < 0.5:
            self.current_dist = (progress / 0.5) * self.range
        else:
            self.current_dist = ((1.0 - progress) / 0.5) * self.range


        cx = int(self.owner.rect.centerx)
        cy = int(self.owner.rect.centery)
        tip_x = int(cx + math.cos(self.base_angle) * self.current_dist)
        tip_y = int(cy + math.sin(self.base_angle) * self.current_dist)

        hit_dir = pygame.math.Vector2(math.cos(self.base_angle), math.sin(self.base_angle))


        #wall colision
        closest_dist = self.current_dist
        hit_wall = False
        if grid:
            start_c = max(0, int((cx - self.range) // TILE_SIZE))
            end_c = min(len(grid[0]) - 1, int((cx + self.range) // TILE_SIZE))
            start_r = max(0, int((cy - self.range) // TILE_SIZE))
            end_r = min(len(grid) - 1, int((cy + self.range) // TILE_SIZE))

            for row in range(start_r, end_r + 1):
                for col in range(start_c, end_c + 1):
                    tile = grid[row][col]
                    if tile.is_obstacle:
                        tile_rect = pygame.Rect(tile.position.x, tile.position.y, TILE_SIZE, TILE_SIZE)
                        clip = tile_rect.clipline((cx, cy), (tip_x, tip_y))
                        if clip:
                            dist = math.hypot(clip[0][0] - cx, clip[0][1] - cy)
                            if dist < closest_dist:
                                closest_dist = dist
                                hit_wall = True

        if hit_wall:
            tip_x = int(cx + math.cos(self.base_angle) * closest_dist)
            tip_y = int(cy + math.sin(self.base_angle) * closest_dist)
            if not getattr(self, "hit_wallx", False):
                self.owner.apply_knockback(-hit_dir, self.knockback_force * 1.2)
                self.owner.shake_req = (10,250)
                self.hit_wallx = True

        self.current_tip_x = tip_x
        self.current_tip_y = tip_y

        for enemy in enemies:
            if enemy not in self.enemies_hit and not enemy.is_dead:
                if enemy.rect.clipline((cx, cy), (tip_x, tip_y)):
                    enemy.take_damage(self.damage, hit_dir, self.knockback_force, self.weapon_name)
                    self.owner.apply_knockback(-hit_dir, self.knockback_force * 0.3)
                    self.enemies_hit.add(enemy)
                    if enemy.is_dead:
                        self.owner.shake_req = (8, 200)
                    else:
                        if not self.owner.shake_req or self.owner.shake_req[0] < 8:
                            self.owner.shake_req = (4,100)


        if chests:
            for chest in chests:
                if chest not in self.enemies_hit and not chest.is_broken:
                    if chest.rect.clipline((cx, cy), (tip_x, tip_y)):
                        chest.break_open()
                        self.enemies_hit.add(chest)

    def draw(self, surface, camera_offset):
        if not self.is_attacking: return

        cx = int(self.owner.rect.centerx - camera_offset.x)
        cy = int(self.owner.rect.centery - camera_offset.y)
        tip_x = int(cx + math.cos(self.base_angle) * self.current_dist)
        tip_y = int(cy + math.sin(self.base_angle) * self.current_dist)

        pygame.draw.line(surface, (150,150,150), (cx, cy), (tip_x, tip_y), 10)



class Player:
    def __init__(self,x,y):
        self.position = pygame.math.Vector2(x,y)
        self.size = TILE_SIZE * 1.5
        self.colour = (0,150,255)

        self.base_speed = 7.0
        self.sprint_mult = 1.55
        self.speed = self.base_speed

        self.max_stamina = 100.0
        self.current_stamina = self.max_stamina
        self.stamina_regen = 0.5
        self.sprint_drain = 0.3
        self.roll_stamina = 15.0

        self.last_exert_t = 0
        self.stamina_regen_delay = 1000
        self.last_exhaust_dmg_t = 0

        self.last_tile_type = 0
        self.tile_entry_t = 0
        self.last_water_t = 0
        self.last_dark_grass_healt_time = 0

        self.lava_tick_rate = 800
        self.last_lava_tick_t = 0

        self.can_attack_tile = True

        self.last_move_dir = pygame.math.Vector2(0,1) # backward tracker for lava knockbak


        #hitbox variables:
        self.hitbox_height = 24
        self.hitbox_width = 24

        self.offset_x = (self.size - self.hitbox_width) // 2
        self.offset_y = (self.size - self.hitbox_height)

        self.rect = pygame.Rect(
            self.position.x + self.offset_x,
            self.position.y + self.offset_y,
            self.hitbox_width,
            self.hitbox_height
        )

        #health and I frame variables:
        self.max_health = 100
        self.current_health = self.max_health
        self.is_invulnerable = False
        self.invulnerability_duration = 1500
        self.last_hit_time = 0

        self.knockback_vector = pygame.math.Vector2(0,0)
        self.weapons = [Sword(self), Spear(self)]
        self.current_weapon_index_idx = 0

        #roll vairables
        self.is_rolling = False
        self.roll_start_time = -2000
        self.roll_duration = 160
        self.roll_speed_multiplier = 2.8
        self.roll_direction = pygame.math.Vector2(0,0)
        self.roll_cooldown = 310
        self.post_roll_blind_duration = 400
        self.last_roll_end_time = 0
        self.is_stunned = False
        self.stun_end_time = 0

        #fatigue variables
        self.is_recovering = False
        self.recovery_start_time = 0
        self.recovery_duration = 1500

        self.shards = 0
        self.shake_req = None

    @property
    def weapon(self):
            return self.weapons[self.current_weapon_index_idx]


    def is_untrackable(self):
        if self.is_rolling:
            return True
        if pygame.time.get_ticks() - self.last_roll_end_time < self.post_roll_blind_duration:
            return True
        return False


    def take_damage(self, amount):
        if self.is_rolling:
            return #hardcoded immunity for roll

        if not self.is_invulnerable:
            self.current_health -= amount
            if self.current_health < 0:
                self.current_health = 0

            self.is_invulnerable = True
            self.last_hit_time = pygame.time.get_ticks()
            self.shake_req = (6,200)

    def apply_knockback(self, direction, force):
        if direction.length() > 0:
            self.knockback_vector += direction.normalize() * force

    def update(self,grid, enemies, chests = None):
        keys = pygame.key.get_pressed() #gets keybs being presed
        current_time = pygame.time.get_ticks()

        center_col = int(self.rect.centerx // TILE_SIZE)
        center_row = int(self.rect.centery // TILE_SIZE)

        center_col = max(0,min(center_col, len(grid[0]) - 1))
        center_row = max(0, min(center_row,len(grid) - 1))
        cur_tile = grid[center_row][center_col]

        if cur_tile.tile_type != self.last_tile_type:
            self.last_tile_type = cur_tile.tile_type
            self.tile_entry_t = current_time

        time_on_tile = current_time - self.tile_entry_t

        can_sprint_tile = True
        can_roll_tile = True
        self.can_attack_tile = True
        current_regen_rate = self.stamina_regen

        effective_regen_delay = self.stamina_regen_delay

        if cur_tile.tile_type == 1: #dark gras
            can_sprint_tile = False
            effective_regen_delay = 200
            if time_on_tile > 2000:
                current_regen_rate = self.stamina_regen * 4.0
            if current_time - self.last_dark_grass_healt_time > 1000:
                self.current_health = min(self.max_health , self.current_health + 4)
                self.last_dark_grass_healt_time = current_time


        elif cur_tile.tile_type == 2:
            can_sprint_tile = False
            can_roll_tile = False
            self.can_attack_tile = False

            if time_on_tile > 3000:
                if current_time - self.last_water_t > 1000:
                    if self.current_stamina > 0:
                        self.current_stamina = max(0.0, self.current_stamina - 0.25)
                        self.last_exert_t = current_time
                    else:
                        if current_time - self.last_water_t > 1000:
                            self.current_health -= 8
                            if self.current_health < 0:
                                self.current_health = 0
                            self.last_water_t =current_time

        is_input_locked =False
        if self.is_stunned:
            if current_time > self.stun_end_time:
                self.is_stunned = False
                self.is_recovering = True
                self.recovery_start_time = current_time
            else:
                is_input_locked = True

        if not self.is_rolling and not is_input_locked:
            if keys[pygame.K_1]: self.current_weapon_index_idx = 0
            if keys[pygame.K_2]: self.current_weapon_index_idx = 1



        # update I frames
        if self.is_invulnerable and not self.is_rolling:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit_time > self.invulnerability_duration:
                self.is_invulnerable = False


        #roll deactivation
        if self.is_rolling:
            if current_time - self.roll_start_time > self.roll_duration:
                self.is_rolling = False
                self.last_roll_end_time = current_time

                # movement
        move_dir = pygame.math.Vector2(0, 0)
        is_sprinting = False
        is_moving = False
        can_roll = False

        if not is_input_locked:
            ##matches pressed keys
            if keys[pygame.K_w]:
                  move_dir.y -= 1
            if keys[pygame.K_s]:
                 move_dir.y += 1
            if keys[pygame.K_a]:
                 move_dir.x -= 1
            if keys[pygame.K_d]:
                move_dir.x += 1
            if move_dir.length() > 0:
                move_dir = move_dir.normalize()
                self.last_move_dir = move_dir

            is_sprinting = keys[pygame.K_LSHIFT] and can_sprint_tile
            is_moving = move_dir.length() > 0
            can_roll = current_time - self.roll_start_time > (self.roll_duration + self.roll_cooldown)

            if keys[pygame.K_SPACE] and not self.is_rolling and self.knockback_vector.length() < 0.5 and can_roll and can_roll_tile and self.current_stamina >= self.roll_stamina:
                self.is_rolling = True
                self.roll_start_time = current_time
                self.current_stamina -= self.roll_stamina
                if move_dir.length() == 0:
                    self.roll_direction = pygame.math.Vector2(1,0)
                else:
                    self.roll_direction = move_dir


        if is_sprinting and is_moving and not self.is_rolling:
            self.last_exert_t = current_time
            if self.current_stamina > 0:
                self.current_stamina = max(0.0, self.current_stamina - self.sprint_drain)
            else:
                if current_time - getattr(self, "last_exhaust_dmg_t", 0) > 1000:
                    self.current_health -= 10
                    if self.current_health < 0:
                        self.current_health = 0
                    self.last_exhaust_dmg_t = current_time

        else:
            if current_time - self.last_exert_t >= effective_regen_delay:
                if not self.is_rolling:
                    self.current_stamina = min(self.max_stamina, self.current_stamina + current_regen_rate)



        speed_modifier = 1.0
        if self.is_recovering:
            elapsed = current_time - self.recovery_start_time
            if elapsed < self.recovery_duration:
                speed_modifier = 0.3 + 0.7 * (elapsed / self.recovery_duration)
            else:
                self.is_recovering = False

        terrain_modifier = getattr(cur_tile, "speed_modifier", 1.0)

        if is_sprinting and is_moving and not self.is_rolling:
            self.speed = self.base_speed * self.sprint_mult * speed_modifier * terrain_modifier
        else:
            self.speed = self.base_speed * speed_modifier * terrain_modifier



        #knockback
        if self.knockback_vector.length() > 0.5:
            self.position.x += self.knockback_vector.x
            self.rect.x = int(self.position.x + self.offset_x)
            self.handle_collisions(grid, "x", self.knockback_vector.x)

            self.position.y += self.knockback_vector.y
            self.rect.y = int(self.position.y + self.offset_y)
            self.handle_collisions(grid, "y", self.knockback_vector.y)

            self.knockback_vector *= 0.85
            if self.knockback_vector.length() < 0.5:
                self.knockback_vector = pygame.math.Vector2(0,0)

        elif self.is_rolling:
            roll_velocity = self.roll_direction * (self.speed * self.roll_speed_multiplier)

            self.position.x += roll_velocity.x
            self.rect.x = int(self.position.x + self.offset_x)
            self.handle_collisions(grid, "x", roll_velocity.x)

            self.position.y += roll_velocity.y
            self.rect.y = int(self.position.y + self.offset_y)
            self.handle_collisions(grid, "y", roll_velocity.y)



        elif not is_input_locked:
            # normal movement
            #x movement
            self.position.x += move_dir.x * self.speed
            self.rect.x = int(self.position.x + self.offset_x)
            self.handle_collisions(grid, "x", move_dir.x)

            #y movement
            self.position.y += move_dir.y * self.speed
            self.rect.y = int(self.position.y + self.offset_y)
            self.handle_collisions(grid, "y", move_dir.y)



        # aena booundaries hard clamp
        map_rows = len(grid)
        map_cols = len(grid[0]) if map_rows > 0 else 0

        max_x = (map_cols * TILE_SIZE) - self.size
        max_y = (map_rows * TILE_SIZE) - self.size

        self.position.x = max(0, min(self.position.x, max_x))
        self.position.y = max(0, min(self.position.y, max_y))

        self.rect.x = int(self.position.x + self.offset_x)
        self.rect.y = int(self.position.y + self.offset_y)

        self.check_hazards(grid)

        if not self.is_rolling and not is_input_locked and self.can_attack_tile:
            self.weapon.update(enemies, chests, grid)


    def get_overlapping_tiles(self, grid):
        left_col = self.rect.left // TILE_SIZE
        right_col = (self.rect.right - 1) // TILE_SIZE
        top_row = self.rect.top // TILE_SIZE
        bottom_row = (self.rect.bottom - 1) // TILE_SIZE

        tiles = []
        for row in range (top_row, bottom_row + 1):
            for col in range (left_col, right_col + 1):
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    if grid[row][col].is_obstacle:
                        tiles.append(grid[row][col])

        return tiles

    def check_hazards(self, grid):
        left_col = self.rect.left // TILE_SIZE
        right_col = (self.rect.right - 1) // TILE_SIZE
        top_row = self.rect.top // TILE_SIZE
        bottom_row = (self.rect.bottom - 1) // TILE_SIZE


        on_lava = False
        for row in range (top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    tilex = grid[row][col]
                    if tilex.tile_type == 3:
                        on_lava = True
                    elif tilex.is_hazard:
                        self.take_damage(10)

        if on_lava:
            current_time =pygame.time.get_ticks()
            if current_time - self.last_lava_tick_t >= self.lava_tick_rate:
                self.take_damage(15)

            if hasattr(self, "last_move_dir") and self.last_move_dir.length() > 0:
                base_dir = - self.last_move_dir
            else:
                base_dir = pygame.math.Vector2(0,-1)


            jump_dir = base_dir.rotate(random.uniform(-60, 60))
            self.apply_knockback(jump_dir,20)
            self.last_lava_tick_t = current_time


    def handle_collisions(self, grid, axis, dir_val):
        if dir_val == 0:
            return

        obstacles = self.get_overlapping_tiles(grid)
        if not obstacles:
            return

        if self.is_rolling:
            self.is_rolling = False
            self.last_roll_end_time = pygame.time.get_ticks()
            self.is_stunned = True

            elapsed = pygame.time.get_ticks() - self.roll_start_time
            intensity = max(0.2, 1.0 - (elapsed / self.roll_duration))
            self.stun_end_time = pygame.time.get_ticks() + int(1500 * intensity)
            self.shake_req = (8,250)

        # x collision
        if axis == "x":
            for tile in obstacles:
                if dir_val > 0:
                    self.rect.right = tile.col * TILE_SIZE
                elif dir_val < 0:
                    self.rect.left = (tile.col + 1) * TILE_SIZE

            self.position.x = self.rect.x - self.offset_x

        # y collision
        elif axis == "y":
            for tile in obstacles:
                if dir_val > 0:
                    self.rect.bottom = tile.row * TILE_SIZE
                elif dir_val < 0:
                    self.rect.top = (tile.row + 1) * TILE_SIZE


            self.position.y = self.rect.y - self.offset_y


    def draw(self, surface, camera_offset):

        #I frame flash effect
        if self.is_invulnerable:
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                return



        draw_x = self.position.x - camera_offset.x
        draw_y = self.position.y - camera_offset.y

        shadow_rect = pygame.Rect(draw_x - 5, draw_y + self.size - 8, self.size + 10, 12)
        pygame.draw.ellipse(surface, (20,20,20), shadow_rect)

        current_colour = self.colour
        if self.is_stunned:
            current_colour = (220,220,50)
            draw_x += random.randint(-3,3)
            draw_y += random.randint(-3,3)
        if self.is_rolling:
            current_colour = (150,200,255)


        pygame.draw.rect(surface,current_colour, (draw_x, draw_y,self.size,self.size))

        if not self.is_rolling and self.can_attack_tile:
            self.weapon.draw(surface, camera_offset)

        #debug with hitbox:
        #hitbox_rect = pygame.Rect(self.rect.x - camera_offset.x, self.rect.y - camera_offset.y, self.rect.width, self.rect.height)
        #pygame.draw.rect(surface, (255,0,0), hitbox_rect, 2)



class Enemy:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x,y)
        self. size = TILE_SIZE // 1.5
        #self.colour = (255,0,0)
        #self.speed = 4
        self.rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)

        #random stress test
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.colour = (r, g, b)

        self.base_speed = random.uniform(2.0, 8)
        self.speed = self.base_speed

        self.damage = 10

        #enemy health variables
        self.max_health = 100
        self.current_health = self.max_health
        self.is_invulnerable = False
        self.invulnerability_duration = 500
        self.last_hit_time = 0
        self.is_dead = False


        #knockback variables
        self.knockback_vector = pygame.math.Vector2(0,0)
        self.is_stunned = False
        self.stun_end_time = 0
        self.last_hit_weapon = None
        self.at_apex = False
        self.apex_end_time = 0
        self.is_recovering = False
        self.recovery_start_time = 0
        self.recovery_duration = 3000

    def take_damage(self, amount, knockback_dir = None, knockback_force = 0, weapon_type = None):
        if not self.is_invulnerable and not self.is_dead:
            if amount > 0 and not self.is_invulnerable:
                self.current_health -= amount
                if self.current_health <= 0:
                    self.current_health = 0
                    self.is_dead = True
                    return

                self.is_invulnerable = True
                self.last_hit_time = pygame.time.get_ticks()

            if knockback_dir and knockback_dir.length() > 0:
                self.knockback_vector = knockback_dir.normalize() * knockback_force
                self.last_hit_weapon = weapon_type
                self.at_apex = False
                self.is_recovering = False


    def update(self, flow_field_grid,grid, max_cols, max_rows, player_center, is_blind):
        current_time = pygame.time.get_ticks()
        # update I frames
        if self.is_invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_hit_time > self.invulnerability_duration:
                self.is_invulnerable = False

        ###### --- knockback physics
        if self.knockback_vector.length() > 0.5:
            old_x, old_y = self.position.x, self.position.y

            #move x
            self.position.x += self.knockback_vector.x
            self.rect.x = int(self.position.x)
            col_x = self.is_colliding(grid)

            #move y
            self.position.y += self.knockback_vector.y
            self.rect.y = int(self.position.y)
            col_y = self.is_colliding(grid)

            #wall impact during knockback
            if col_x or col_y:
                self.position.x, self.position.y = old_x, old_y
                self.rect.topleft = (int(old_x), int(old_y))
                self.knockback_vector = pygame.math.Vector2(0,0)

                if self.last_hit_weapon == "Sword":
                    self.is_stunned = True
                    self.stun_end_time = current_time + 3000 # time that enemy remains stunned
                elif self.last_hit_weapon == "Spear":
                    self.current_health = 0
                    self.is_dead = True
                else:
                    self.knockback_vector *= 0.85
                    if self.knockback_vector.length() < 0.5:
                        self.knockback_vector = pygame.math.Vector2(0,0)

                return # skip pathfinder while colliding


            #open space friction
            self.knockback_vector *= 0.85
            if self.knockback_vector.length() < 0.5:
                self.knockback_vector = pygame.math.Vector2(0,0)
                self.at_apex = True
                self.apex_end_time = current_time + 400

            return

        #### ---- STUNNED ENEMY
        if self.is_stunned:
            if current_time > self.stun_end_time:
                self.is_stunned = False
            else:
                return # skips pathfinder here asw

        if self.at_apex:
            if current_time < self.apex_end_time:
                return
            else:
                self.at_apex = False
                self.is_recovering = True
                self.recovery_start_time = current_time
                if self.last_hit_weapon == "Sword":
                    self.recovery_duration = 5000
                else:
                    self.recovery_duration = 2800

        speed_modifier = 1.0
        if self.is_recovering:
            elapsed = current_time - self.recovery_start_time
            if elapsed < self.recovery_duration:
                speed_modifier = elapsed / self.recovery_duration
            else:
                self.is_recovering =False



        dist = float("inf")
        dive_multiplier = 1.0

        if not is_blind:
            dx = player_center[0] - self.rect.centerx
            dy = player_center[1] - self.rect.centery
            dist = math.hypot(dx, dy)

            if dist < 150 and not self.is_recovering:
                dive_multiplier = 1.0 + ((150 - dist) / 150) * 1.8


        col = int(self.rect.centerx // TILE_SIZE)
        row = int(self.rect.centery // TILE_SIZE)

        col = max(0, min(col , max_cols - 1))
        row = max(0, min (row, max_rows - 1))

        terrain_modifier = getattr(grid[row][col], "speed_modifier", 1.0)

        self.speed = self.base_speed * speed_modifier * dive_multiplier * terrain_modifier


        if dist < TILE_SIZE*2.5 and dist > 0 and not is_blind:
            dx = player_center[0] - self.rect.centerx
            dy = player_center[1] - self.rect.centery
            move_dir = pygame.math.Vector2(dx, dy).normalize()
        else:
            col = int(self.rect.centerx // TILE_SIZE)
            row = int(self.rect.centery // TILE_SIZE)

            col = max(0, min(col, max_cols - 1))
            row = max(0, min(row, max_rows - 1))

            move_dir = flow_field_grid[row][col]


        #standard pathfinde nav


        if move_dir.length() > 0:
            move_dir = move_dir.normalize()

            self.position.x += move_dir.x * self.speed
            self.rect.x = int(self.position.x)
            if self.is_colliding(grid):
                self.position.x -= move_dir.x * self.speed
                self.rect.x = int(self.position.x)

            self.position.y += move_dir.y * self.speed
            self.rect.y = int(self.position.y)
            if self.is_colliding(grid):
                self.position.y -= move_dir.y * self.speed
                self.rect.y = int(self.position.y)

        self.rect.topleft = (round(self.position.x), round(self.position.y))


    def is_colliding(self, grid):
        #calc grid coordinates of player boundary
        left_col = int(self.rect.left // TILE_SIZE)
        right_col = int((self.rect.right - 1)// TILE_SIZE)
        top_row = int(self.rect.top // TILE_SIZE)
        bottom_row = int((self.rect.bottom - 1 )// TILE_SIZE)

        #loop thru every tiles player is touchibg
        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    if grid[row][col].is_obstacle:
                        return True

        return False


    def draw(self, surface, camera_offset):
        draw_x = self.position.x - camera_offset.x
        draw_y = self.position.y - camera_offset.y

        ## enenmy jitter stun effect
        if self.is_stunned:
            draw_x += random.randint(-3,3)
            draw_y += random.randint(-3,3)

        current_colour = self.colour
        if self.is_invulnerable:
            if (pygame.time.get_ticks() // 50) % 5 == 0:
                current_colour = (255,255,255)

        elif self.is_stunned:
            if (pygame.time.get_ticks() // 150) % 5 == 0:
                current_colour = (220,220,50) #subtle yellow for stunned enemy


        pygame.draw.rect(surface, current_colour, (draw_x, draw_y, self.size, self.size))

        # conditional floating health bar
        if 0 < self.current_health < self.max_health:
            bar_width = 24
            bar_height = 4

            ## position 8 pixels above enemy
            bar_x = draw_x + (self.size / 2) - (bar_width / 2)
            bar_y = draw_y - 18

            ##multi layer health border
            ###outer black
            pygame.draw.rect(surface, (0,0,0), (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6))
            ###middle white
            pygame.draw.rect(surface, (255,255,255), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
            ###outer black
            pygame.draw.rect(surface, (0,0,0), (bar_x - 1, bar_y -1, bar_width + 2, bar_height +2))

            ##grey background health bar
            pygame.draw.rect(surface, (60,60,60), (bar_x, bar_y, bar_width, bar_height))

            ##foreground (red health
            ###health ratio
            health_ratio = self.current_health / self.max_health
            ### rendering
            current_width = max(1, int(bar_width * health_ratio))
            pygame.draw.rect(surface, (160,15,35), (bar_x, bar_y, current_width, bar_height))


class Chest:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x,y)
        self.size = TILE_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.is_broken = False
        self.has_dropped = False

    def break_open(self):
        self.is_broken = True


    def draw(self, surface, camera_offset):
        draw_x = self.position.x - camera_offset.x
        draw_y = self.position.y - camera_offset.y
        if not self.is_broken:
            pygame.draw.rect(surface, (139,69,19), (draw_x, draw_y, self.size, self.size))
            pygame.draw.rect(surface, (218,165,32), (draw_x, draw_y + 8, self.size, 8))
        else:
            pygame.draw.rect(surface, (100,50,10), (draw_x, draw_y + self.size - 10, self.size, 10))

class Shard:
    def __init__(self, x, y, floor_y=None):
        if floor_y is None:
            floor_y =y

        self.position = pygame.math.Vector2(x - 12, y - 12)
        self.rect = pygame.Rect(self.position.x, self.position.y, 24,24)
        self.base_y = floor_y + random.randint(-15,25)
        angle = random.uniform(math.pi * 1.05, math.pi * 1.85)
        speed = random.uniform(3,8)
        self.velocity = pygame.math.Vector2(math.cos(angle) * speed, - random.uniform(4, 8))
        self.grav = 0.5
        self.spawn_time = 0
        self.state = "DROPPING"
        self.hover_start_time = 0
        self.screen_pos = pygame.math.Vector2(0,0)
        self.bounce_count = 0

    def collect(self, camera_offset):
        if self.state in ["IDLE", "DROPPING"]:
            self.state = "HOVER"
            self.hover_start_time = pygame.time.get_ticks()
            self.screen_pos.x = self.position.x - camera_offset.x
            self.screen_pos.y = self.position.y - camera_offset.y

            self.velocity.y = -10
            self.velocity.x = random.uniform(-2,2)
            self.rect.width = 0
            self.rect.height = 0

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == "DROPPING":
            self.velocity.y += self.grav
            self.position += self.velocity

            if self.position.y >= self.base_y and self.velocity.y > 0:
                self.position.y = self.base_y
                self.velocity.y *= -0.5
                self.velocity.x *= 0.6
                self.bounce_count += 1

                if abs(self.velocity.y) < 1.0:
                    self.state = "IDLE"
                    self.spawn_time = current_time

            self.rect.topleft = (int(self.position.x), int(self.position.y))
            return False

        elif self.state == "IDLE":
            offset = math.sin((pygame.time.get_ticks() - self.spawn_time) * 0.005) * 5
            self.position.y = self.base_y + offset
            self.rect.y = int(self.position.y)
            return False

        elif self.state == "HOVER":
            self.velocity.y += 0.8
            self.screen_pos += self.velocity
            if current_time - self.hover_start_time > 200:
                self.state = "FLYING"
            return False

        elif self.state == "FLYING":
            target_x, target_y = ARENA_BOUND_X - 60, 20
            dx = target_x - self.screen_pos.x
            dy = target_y - self.screen_pos.y
            dist = math.hypot(dx,dy)

            if dist < 30:
                return True
            else:
                move_dir = pygame.math.Vector2(dx, dy).normalize()
                speed = max(6.0, dist * 0.08)
                self.screen_pos += move_dir * speed
            return False

    def draw(self, surface, camera_offset, icon):
        if self.state in ["IDLE", "DROPPING"]:
            draw_x = self.position.x - camera_offset.x
            draw_y = self.position.y - camera_offset.y
            surface.blit(icon, (draw_x, draw_y))
        else:
            surface.blit(icon, (self.screen_pos.x, self.screen_pos.y))

class FloatReward:
    def __init__(self, x, y, text, icon):
        self.x = x
        self.y = y
        self.text = text
        self.icon = icon
        self.start_time = pygame.time.get_ticks()
        self.duration = 1000

    def update(self):
        self.y -= 0.5
        return pygame.time.get_ticks() - self.start_time > self.duration

    def draw(self, surface, camera_offset, font):
        draw_x = self.x - camera_offset.x
        draw_y = self.y - camera_offset.y
        surface.blit(self.icon, (draw_x, draw_y))

        text_white = font.render(self.text, True, (255,255,255))
        text_black = font.render(self.text, True, (0,0,0))

        t_x = draw_x + 28
        t_y = draw_y + 4

        surface.blit(text_black, (t_x - 2, t_y))
        surface.blit(text_black, (t_x +2, t_y))
        surface.blit(text_black, (t_x , t_y- 2))
        surface.blit(text_black, (t_x , t_y + 2))
        surface.blit(text_white, (t_x , t_y))


        text_surf = font.render(self.text, True, (255, 255,255))
        surface.blit(text_surf, (draw_x + 28, draw_y + 4))


class Death:
    def __init__(self, x ,y, colour):
        self.x = x
        self.y = y
        self.colour = colour
        self.radius = 2
        self.alpha = 255

    def update(self):
        self.radius +=3
        self.alpha = max(0, self.alpha -15)
        return self.alpha <= 0

    def draw(self,surface, camera_offset):
        if self.alpha > 0:
            temp_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            r,g, b = self.colour

            pygame.draw.circle(temp_surf, (r,g,b , int(self.alpha * 0.6)), (self.radius, self.radius), self.radius)
            pygame.draw.circle(temp_surf, (255,255,255, self.alpha), (self.radius,self.radius),self.radius,2)

            draw_x = self.x - camera_offset.x - self.radius
            draw_y = self.y - camera_offset.y - self.radius
            surface.blit(temp_surf, (draw_x,draw_y))

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((ARENA_BOUND_X,ARENA_BOUND_Y))
        pygame.display.set_caption("Shacklegeist")
        self.clock = pygame.time.Clock()

        self.state = GameState.MENU

        #menu nav options
        self.menu_options = ["PLAY-GAME","TRAINING-RANGE","SETTINGS"]
        self.hovered_option = None

        self.current_level = 1
        self.active_enemies = []
        self.player = Player(50,50)

        self.camera = Camera()

        #map
        self.grid = self.create_oop_grid()


        #pathfinding:
        map_rows = len(self.grid)
        map_cols = len(self.grid[0]) if map_rows > 0 else 0

        self.pathfinder = Pathfinder(map_cols, map_rows)


        try:
            self.emerald_icon = pygame.image.load("emerald.png").convert_alpha()
            self.emerald_icon = pygame.transform.scale(self.emerald_icon, (24,24))
        except FileNotFoundError:
            print("no emerald image")
            self.emerald_icon = pygame.Surface((24,24), pygame.SRCALPHA)
            pygame.draw.polygon(self.emerald_icon, (0,40, 10), [(8,2),(16, 2), (22 ,8),(22 , 16), (16,22), (8,22),(2,16),(2,8)])
            pygame.draw.polygon(self.emerald_icon, (10,140, 50), [(8,4),(16, 4), (20 ,8),(20 , 16), (16,20),(8,20),(4,16), (4,8)])
            pygame.draw.polygon(self.emerald_icon, (30,210, 100), [(8,6),(14, 6), (18 ,10),(18 , 16), (14,18), (8,18), (6,16),(6,10)])
            pygame.draw.polygon(self.emerald_icon, (220,255, 230), [(8,6),(12, 6), (10 ,10),(6 , 10)])

        ### enemies stress test
        for _ in range(10):
            random_x = random.randint(50, 1500)
            random_y = random.randint(50,1500)
            self.active_enemies.append(Enemy(random_x, random_y))


        self.chests = []
        for _ in range(10):
            self.chests.append(Chest(random.randint(150,1500), random.randint(150,1500)))


        self.shards_active = []
        for _ in range (5):
            self.shards_active.append(Shard(random.randint(100,300), random.randint(100,250)))

        self.floating_texts = []
        self.death_effects = []

        try:
            self.bg_image = pygame.image.load("menu_bg.png").convert()

            bg_height = ARENA_BOUND_Y
            bg_width = int(self.bg_image.get_width() * (bg_height / self.bg_image.get_height()))
            self.bg_image = pygame.transform.smoothscale(self.bg_image, (bg_width, bg_height))

        except FileNotFoundError:
            print("No image found")
            self.bg_image = pygame.Surface((ARENA_BOUND_X, ARENA_BOUND_Y))
            self.bg_image.fill((20,20,25))

        self.bg_scroll = 0


    # create map with objects
    def create_oop_grid(self):
        oop_grid = [] #initialise arraw

        #this is a essentially a double for loop adding each tile to the oop_grid array
        for row_index, row in enumerate(GRID_MAP):
            grid_row = []
            for col_index, tile_type in enumerate(row):
                grid_row.append(Tile(col_index,row_index,tile_type))
            oop_grid.append(grid_row)
        return oop_grid

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    self.hovered_option = None

                    for i in range(len(self.menu_options)):
                        hitbox = pygame.Rect(0, 0, 400, 60)
                        hitbox.center = (ARENA_BOUND_X // 2, 400 + (i * 80))

                        if hitbox.collidepoint(mouse_pos):
                            self.hovered_option = i


                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: #left click
                        if getattr(self, "hovered_option", None) is not None:
                            if self.hovered_option == 0:
                                self.state = GameState.PLAYING

            elif self.state == GameState.PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.player.is_rolling and self.player.can_attack_tile and not self.player.is_stunned:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            world_x = mouse_x + self.camera.offset.x
                            world_y = mouse_y + self.camera.offset.y

                            self.player.weapon.attack((world_x, world_y))




            elif self.state == GameState.GAMEOVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__init__()


    def update(self):

        if self.state == GameState.MENU:
            self.bg_scroll -= 0.3 # adjust for faster/slower pan

            bg_width = self.bg_image.get_width()
            if self.bg_scroll <= -bg_width:
                self.bg_scroll = 0

        elif self.state == GameState.PLAYING:
            self.player.update(self.grid, self.active_enemies, self.chests)

            if self.player.shake_req:
                intensity, duration = self.player.shake_req
                self.camera.start_shake(intensity,duration)
                self.player.shake_req = None

            map_rows = len(self.grid)
            map_cols = len(self.grid[0]) if map_rows > 0 else 0

            self.camera.update(self.player, map_cols, map_rows)

            is_blind = self.player.is_untrackable()

            ## update enemies and pathfinder
            if not is_blind:
                self.pathfinder.generate_flow_field(self.grid, self.player.rect)

            for enemy in self.active_enemies:
                enemy.update(self.pathfinder.flow_field,self.grid, map_cols, map_rows, self.player.rect.center, is_blind)

                #check player hitbox overlap with enemy:
                if self.player.rect.colliderect(enemy.rect) and not self.player.is_rolling:
                    self.player.take_damage(enemy.damage)

                    ##bodyslam physics
                    bump_dx = self.player.rect.centerx - enemy.rect.centerx
                    bump_dy = self.player.rect.centery - enemy.rect.centery
                    bump_dir = pygame.math.Vector2(bump_dx, bump_dy)

                    if bump_dir.length() > 0:
                        bump_dir = bump_dir.normalize()
                        self.player.apply_knockback(bump_dir, 8)
                        enemy.take_damage(0, -bump_dir, 15, "Body Slam")

            surviving_enemies =[]
            for enemy in self.active_enemies:
                if enemy.is_dead:
                    self.player.current_stamina = self.player.max_stamina
                    self.player.current_health = min(self.player.max_health, self.player.current_health + (self.player.max_health * 0.08))
                    self.death_effects.append(Death(enemy.rect.centerx, enemy.rect.centery, enemy.colour))
                    num_drops = random.randint(1,3)
                    for _ in range(num_drops):
                        self.shards_active.append(Shard(enemy.rect.centerx, enemy.rect.centery, enemy.rect.bottom))
                else:
                    surviving_enemies.append(enemy)
            self.active_enemies = surviving_enemies


            #chest explosion
            for chest in self.chests:
                if chest.is_broken and not chest.has_dropped:
                    chest.has_dropped = True
                    num_drops = random.randint(5,8)
                    for _ in range(num_drops):
                        drop_x = chest.rect.centerx
                        drop_y = chest.rect.centery
                        self.shards_active.append(Shard(drop_x,drop_y,chest.rect.bottom))


            #shard collection
            remaining_shards = []
            for shard in self.shards_active:
                if shard.state in  ["IDLE","DROPPING"]:
                    shard.update()
                    if self.player.rect.colliderect(shard.rect):
                        shard.collect(self.camera.offset)
                    remaining_shards.append(shard)
                else:
                    arrived = shard.update()
                    if arrived:
                        self.player.shards += 1
                        self.player.current_health = min(self.player.max_health, self.player.current_health + (self.player.max_health * 0.04))
                    else:
                        remaining_shards.append(shard)

            self.shards_active = remaining_shards

            self.floating_texts = [ft for ft in self.floating_texts if not ft.update()]
            self.death_effects = [fx for fx in self.death_effects if not fx.update()]

            # game over chjeck
            if self.player.current_health <= 0:
                self.state = GameState.GAMEOVER


    def draw_ui(self):

        #health bar text
        font = pygame.font.SysFont("courier", 36, bold=True)

        # HEALTH
        ## health text
        text_str = "HEALTH"
        text_white = font.render(text_str, True, (255,255,255))
        text_black = font.render(text_str, True, (0,0,0))

        text_x, text_y = 20,15

        ### black text shifted in each direction by 2 pixels to give 2 pixel utline
        self.screen.blit(text_black, (text_x - 2, text_y))
        self.screen.blit(text_black, (text_x + 2, text_y))
        self.screen.blit(text_black, (text_x, text_y - 2))
        self.screen.blit(text_black, (text_x, text_y + 2))

        ### white text in centre of black
        self.screen.blit(text_white, (text_x, text_y))

        ## health bar

        ###inner health
        bar_x = 26
        bar_y = 55
        bar_width = 200
        bar_height = 20

        ###health bar background 3 layers
        #### outer black
        pygame.draw.rect(self.screen, (0,0,0), (bar_x - 6, bar_y - 6, bar_width + 12, bar_height + 12))
        #### middle white
        pygame.draw.rect(self.screen, (255,255,255), (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8))
        #### inner black
        pygame.draw.rect(self.screen, (0,0,0), (bar_x- 2, bar_y - 2, bar_width + 4, bar_height + 4))

        ### actual inner fill of health bar
        #### grey background
        pygame.draw.rect(self.screen, (60,60,60), (bar_x, bar_y, bar_width, bar_height))


        ####player health ratio remaining
        health_ratio = self.player.current_health / self.player.max_health

        ####red foreground for remaining health
        if health_ratio > 0:
            fg_rect = pygame.Rect(bar_x, bar_y, bar_width * health_ratio, bar_height)
            pygame.draw.rect(self.screen, (160, 15, 35), fg_rect)


        num_chunks = 5
        chunk_width = bar_width / num_chunks

        for i in range(1, num_chunks):
            line_x = bar_x + (i * chunk_width)
            pygame.draw.line(self.screen, (0,0,0), (line_x, bar_y), (line_x, bar_y + bar_height), 2)



        ## STAMINA HUD
        stamina_str = "STAMINA"
        stamina_white = font.render(stamina_str, True, (255,255,255))
        stamina_black = font.render(stamina_str, True, (0,0,0))

        stamina_x, stamina_y = 20, ARENA_BOUND_Y -60

        self.screen.blit(stamina_black, (stamina_x - 2, stamina_y))
        self.screen.blit(stamina_black, (stamina_x+ 2, stamina_y))
        self.screen.blit(stamina_black, (stamina_x, stamina_y - 2 ))
        self.screen.blit(stamina_black, (stamina_x , stamina_y+ 2))
        self.screen.blit(stamina_white, (stamina_x , stamina_y))

        st_bar_x = 26
        st_bar_y = ARENA_BOUND_Y - 20
        st_bar_width = 150
        st_bar_height = 12

        pygame.draw.rect(self.screen, (0,0,0), (st_bar_x - 3, st_bar_y - 3, st_bar_width + 6, st_bar_height + 6))
        pygame.draw.rect(self.screen, (255,255,255), (st_bar_x - 2, st_bar_y - 2, st_bar_width + 4, st_bar_height + 4))
        pygame.draw.rect(self.screen, (0, 0, 0), (st_bar_x - 1, st_bar_y - 1, st_bar_width + 2, st_bar_height + 2))

        pygame.draw.rect(self.screen, (60,60,60), (st_bar_x, st_bar_y, st_bar_width, st_bar_height))

        stamina_ratio = self.player.current_stamina / self.player.max_stamina
        if stamina_ratio > 0:
            bruh = pygame.Rect(st_bar_x, st_bar_y, st_bar_width * stamina_ratio, st_bar_height)

            if self.player.is_recovering or self.player.is_stunned:
                if (pygame.time.get_ticks() // 150) % 2 == 0:
                    bar_colour = (255,220,50)
                else:
                    bar_colour = (100,150,30)
            else:
                bar_colour = (50,150,255)

            pygame.draw.rect(self.screen, bar_colour, bruh)

        ## weapon HUD
        weapon_txt = f"WEAPON: {self.player.weapon.weapon_name} (Press 1 or 2)"
        w_text_white = font.render(weapon_txt, True, (255,255,255))
        w_text_black = font.render(weapon_txt, True, (0,0,0))
        w_text_y = 90


        ## black outline
        self.screen.blit(w_text_black, (text_x - 2, w_text_y))
        self.screen.blit(w_text_black, (text_x + 2, w_text_y))
        self.screen.blit(w_text_black, (text_x, w_text_y - 2))
        self.screen.blit(w_text_black, (text_x, w_text_y + 2))

        ## white inside
        self.screen.blit(w_text_white, (text_x, w_text_y))

        #SHARD UI
        shard_font = pygame.font.SysFont("courier", 42, bold=True)
        shard_str = str(self.player.shards)
        shard_white = shard_font.render(shard_str, True, (255,255,255))
        shard_black = shard_font.render(shard_str, True, (0,0,0))

        s_x = ARENA_BOUND_X - 60
        s_y = 20

        text_rect = shard_white.get_rect(topleft=(s_x,s_y))
        icon_rect = self.emerald_icon.get_rect(midright = (text_rect.left - 8, text_rect.centery))

        self.screen.blit(shard_black, (s_x - 2, s_y))
        self.screen.blit(shard_black, (s_x+2, s_y))
        self.screen.blit(shard_black, (s_x , s_y -2))
        self.screen.blit(shard_black, (s_x , s_y+2))
        self.screen.blit(shard_white, (s_x, s_y))

        self.screen.blit(self.emerald_icon, icon_rect)

    def draw_menu(self):
        # scrolling background
        bg_width = self.bg_image.get_width()
        self.screen.blit(self.bg_image, (int(self.bg_scroll), 0))
        self.screen.blit(self.bg_image, (int(self.bg_scroll) + bg_width, 0))

        #title with retro outline
        title_font = pygame.font.SysFont("courier", 100, bold=True)
        title_str = "SHACKLEGEIST"
        title_white = title_font.render(title_str, True, (255, 255, 255))
        title_black = title_font.render(title_str, True, (0,0,0))

        title_rect = title_white.get_rect(center = (ARENA_BOUND_X // 2, 200))

        ## black in 4 positions for outline
        self.screen.blit(title_black, (title_rect.x - 4, title_rect.y))
        self.screen.blit(title_black, (title_rect.x + 4, title_rect.y))
        self.screen.blit(title_black, (title_rect.x, title_rect.y - 4))
        self.screen.blit(title_black, (title_rect.x, title_rect.y + 4))

        ## white fill text
        self.screen.blit(title_white, title_rect)

        # menu options with dynamic hover

        option_font = pygame.font.SysFont("courier", 60, bold=True)

        for i, option_text in enumerate(self.menu_options):
            base_y = 400 + (i * 80)

            if i == self.hovered_option:
                colour = (170, 170, 170)
                draw_y = base_y - 4
            else:
                colour = (255,255,255)
                draw_y = base_y

            text_surf = option_font.render(option_text, True, colour)
            text_black = option_font.render(option_text, True, (0,0,0))

            text_rect = text_surf.get_rect(center =(ARENA_BOUND_X // 2, draw_y))

            self.screen.blit(text_black, (text_rect.x - 3, text_rect.y))
            self.screen.blit(text_black, (text_rect.x + 3, text_rect.y))
            self.screen.blit(text_black, (text_rect.x, text_rect.y - 3))
            self.screen.blit(text_black, (text_rect.x, text_rect.y + 3))



            self.screen.blit(text_surf, text_rect)



    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()

        elif self.state == GameState.PLAYING or self.state == GameState.GAMEOVER:

            self.screen.fill((30,30,30))


            # finding the top row and leftmost column
            start_col = max(0, int(self.camera.offset.x // TILE_SIZE))
            start_row = max(0, int(self.camera.offset.y // TILE_SIZE))

            # finding the bottom row and rightmost column
            end_col = min(len(self.grid[0]), int((self.camera.offset.x + ARENA_BOUND_X)// TILE_SIZE + 2))
            end_row = min(len(self.grid), int((self.camera.offset.y + ARENA_BOUND_Y)// TILE_SIZE + 2))

            for row in range(start_row, end_row):
                for col in range(start_col,end_col):
                    tile = self.grid[row][col]
                    tile.draw(self.screen, self.camera.offset)


            for chest in self.chests:
                chest.draw(self.screen, self.camera.offset)

            for shard in self.shards_active:
                shard.draw(self.screen, self.camera.offset, self.emerald_icon)

            #draw enemies
            for enemy in self.active_enemies:
                enemy.draw(self.screen, self.camera.offset)

            for darrow in self.death_effects:
                darrow.draw(self.screen, self.camera.offset)


            text_font = pygame.font.SysFont("courier", 34, bold=True)
            for ft in self.floating_texts:
                ft.draw(self.screen,self.camera.offset, text_font)


            # player
            if self.state == GameState.PLAYING:
                self.player.draw(self.screen, self.camera.offset)
                self.draw_ui()

            elif self.state == GameState.GAMEOVER:
                overlay = pygame.Surface((ARENA_BOUND_X, ARENA_BOUND_Y))
                overlay.set_alpha(150)
                overlay.fill((0,0,0))
                self.screen.blit(overlay, (0,0))

                font = pygame.font.SysFont("courier", 60, bold=True)
                text_surf = font.render("YOU DIED", True, (255,50,50))
                text_rect = text_surf.get_rect(center = (ARENA_BOUND_X // 2, ARENA_BOUND_Y // 2 ))
                self.screen.blit(text_surf, text_rect)

                small_font = pygame.font.SysFont("courier", 40, bold=True)
                restart_surf = small_font.render("Press ENTER to Restart", True, (255,255,255))
                restart_rect = restart_surf.get_rect(center = (ARENA_BOUND_X // 2, ARENA_BOUND_Y // 2 + 50))
                self.screen.blit(restart_surf, restart_rect)

        pygame.display.flip()


    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)




if __name__ == "__main__":
    shacklegeist = Game()
    shacklegeist.run()




