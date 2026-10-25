import pygame
import random
import sys

# --- Constants ---
WIDTH, HEIGHT = 900, 300
FPS = 180
GROUND_Y = 240
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GREY = (180, 180, 180)
DARK_GREY = (100, 100, 100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Runner")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont("monospace", 48, bold=True)
font_med = pygame.font.SysFont("monospace", 22)
font_small = pygame.font.SysFont("monospace", 16)


# --- Dino ---
class Dino:
    W, H = 40, 52
    JUMP_V = -14
    GRAVITY = 0.7
    DUCK_H = 28

    def __init__(self):
        self.x = 80
        self.reset()

    def reset(self):
        self.y = GROUND_Y - self.H
        self.vy = 0
        self.on_ground = True
        self.ducking = False
        self.dead = False
        # Animation frames (drawn procedurally)
        self.frame = 0
        self.frame_timer = 0

    def jump(self):
        if self.on_ground and not self.dead:
            self.vy = self.JUMP_V
            self.on_ground = False

    def duck(self, ducking):
        self.ducking = ducking and self.on_ground

    def update(self):
        if not self.on_ground:
            self.vy += self.GRAVITY
            self.y += self.vy
            ground = GROUND_Y - (self.DUCK_H if self.ducking else self.H)
            if self.y >= ground:
                self.y = ground
                self.vy = 0
                self.on_ground = True

        # Leg animation
        self.frame_timer += 1
        if self.frame_timer >= 8:
            self.frame = 1 - self.frame
            self.frame_timer = 0

    def get_rect(self):
        h = self.DUCK_H if self.ducking else self.H
        return pygame.Rect(self.x + 4, self.y + 4, self.W - 8, h - 8)

    def draw(self, surf):
        h = self.DUCK_H if self.ducking else self.H
        col = BLACK
        # Body
        body_rect = pygame.Rect(self.x, self.y, self.W, h)
        pygame.draw.rect(surf, col, body_rect, border_radius=6)
        # Eye
        eye_x = self.x + self.W - 10
        eye_y = self.y + 8
        pygame.draw.circle(surf, WHITE, (eye_x, eye_y), 5)
        pygame.draw.circle(surf, col, (eye_x + 1, eye_y), 2)
        # Legs (only when on ground)
        if self.on_ground and not self.ducking:
            leg_y = self.y + h
            if self.frame == 0:
                pygame.draw.rect(surf, col, (self.x + 6, leg_y, 8, 10))
                pygame.draw.rect(surf, col, (self.x + 22, leg_y - 6, 8, 10))
            else:
                pygame.draw.rect(surf, col, (self.x + 6, leg_y - 6, 8, 10))
                pygame.draw.rect(surf, col, (self.x + 22, leg_y, 8, 10))


# --- Cactus ---
class Cactus:
    TYPES = [
        {"w": 20, "h": 50, "arms": 1},
        {"w": 28, "h": 42, "arms": 2},
        {"w": 36, "h": 55, "arms": 2},
    ]

    def __init__(self, x):
        t = random.choice(self.TYPES)
        self.w = t["w"]
        self.h = t["h"]
        self.arms = t["arms"]
        self.x = x
        self.y = GROUND_Y - self.h

    def update(self, speed):
        self.x -= speed

    def get_rect(self):
        return pygame.Rect(self.x + 4, self.y + 4, self.w - 8, self.h - 8)

    def draw(self, surf):
        col = BLACK
        # Main trunk
        pygame.draw.rect(surf, col, (self.x + self.w // 2 - 6, self.y, 12, self.h), border_radius=3)
        # Arms
        arm_y = self.y + self.h // 3
        if self.arms >= 1:
            pygame.draw.rect(surf, col, (self.x, arm_y, self.w // 2 - 2, 10), border_radius=3)
            pygame.draw.rect(surf, col, (self.x, arm_y - 14, 10, 18), border_radius=3)
        if self.arms >= 2:
            pygame.draw.rect(surf, col, (self.x + self.w // 2 + 2, arm_y + 8, self.w // 2, 10), border_radius=3)
            pygame.draw.rect(surf, col, (self.x + self.w - 10, arm_y - 6, 10, 18), border_radius=3)

    def off_screen(self):
        return self.x + self.w < 0


# --- Bird ---
class Bird:
    W, H = 38, 22
    HEIGHTS = [GROUND_Y - 80, GROUND_Y - 110, GROUND_Y - 50]

    def __init__(self, x):
        self.x = x
        self.y = random.choice(self.HEIGHTS)
        self.flap = 0
        self.flap_timer = 0

    def update(self, speed):
        self.x -= speed
        self.flap_timer += 1
        if self.flap_timer >= 10:
            self.flap = 1 - self.flap
            self.flap_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x + 4, self.y + 4, self.W - 8, self.H - 8)

    def draw(self, surf):
        col = BLACK
        # Body
        pygame.draw.ellipse(surf, col, (self.x + 8, self.y + 6, 22, 12))
        # Beak
        pygame.draw.polygon(surf, col, [(self.x + 30, self.y + 10), (self.x + 38, self.y + 11), (self.x + 30, self.y + 14)])
        # Wings
        wing_y = self.y + 2 if self.flap == 0 else self.y + 12
        pygame.draw.ellipse(surf, col, (self.x + 4, wing_y, 20, 10))

    def off_screen(self):
        return self.x + self.W < 0


# --- Cloud ---
class Cloud:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(30, 100)
        self.w = random.randint(60, 120)

    def update(self, speed):
        self.x -= speed * 0.3

    def draw(self, surf):
        pygame.draw.ellipse(surf, GREY, (self.x, self.y, self.w, 25))
        pygame.draw.ellipse(surf, GREY, (self.x + 15, self.y - 12, self.w - 20, 25))
        pygame.draw.ellipse(surf, GREY, (self.x + self.w - 40, self.y - 6, 50, 22))

    def off_screen(self):
        return self.x + self.w < 0


# --- Game State ---
class Game:
    INIT_SPEED = 6.0
    MAX_SPEED = 16.0
    SPEED_INC = 0.002

    def __init__(self):
        self.reset()

    def reset(self):
        self.dino = Dino()
        self.obstacles = []
        self.clouds = [Cloud(random.randint(100, WIDTH)) for _ in range(3)]
        self.speed = self.INIT_SPEED
        self.score = 0
        self.hi_score = getattr(self, 'hi_score', 0)
        self.spawn_timer = 0
        self.spawn_interval = 90
        self.game_over = False
        self.started = False
        # Ground line dots
        self.ground_dots = [(random.randint(0, WIDTH), GROUND_Y + random.randint(2, 10)) for _ in range(30)]

    def spawn_obstacle(self):
        x = WIDTH + 20
        # After score 300, birds appear
        if self.score > 300 and random.random() < 0.3:
            self.obstacles.append(Bird(x))
        else:
            self.obstacles.append(Cactus(x))

    def update(self):
        if self.game_over or not self.started:
            return

        self.speed = min(self.MAX_SPEED, self.INIT_SPEED + self.score * self.SPEED_INC)
        self.score += 1

        self.dino.update()

        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
            self.spawn_interval = random.randint(60, 110)

        # Update obstacles
        for obs in self.obstacles:
            obs.update(self.speed)
        self.obstacles = [o for o in self.obstacles if not o.off_screen()]

        # Update clouds
        for cloud in self.clouds:
            cloud.update(self.speed)
        self.clouds = [c for c in self.clouds if not c.off_screen()]
        if len(self.clouds) < 4 and random.random() < 0.01:
            self.clouds.append(Cloud(WIDTH + 10))

        # Move ground dots
        self.ground_dots = [(x - self.speed, y) for x, y in self.ground_dots]
        self.ground_dots = [(x if x > 0 else x + WIDTH, y) for x, y in self.ground_dots]

        # Collision
        for obs in self.obstacles:
            if self.dino.get_rect().colliderect(obs.get_rect()):
                self.game_over = True
                self.hi_score = max(self.hi_score, self.score // 10)

    def draw(self):
        screen.fill(WHITE)

        # Clouds
        for cloud in self.clouds:
            cloud.draw(screen)

        # Ground
        pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
        for x, y in self.ground_dots:
            pygame.draw.circle(screen, GREY, (int(x), int(y)), 2)

        # Obstacles
        for obs in self.obstacles:
            obs.draw(screen)

        # Dino
        self.dino.draw(screen)

        # Score
        score_surf = font_med.render(f"HI {self.hi_score:05d}  {self.score // 10:05d}", True, DARK_GREY)
        screen.blit(score_surf, (WIDTH - score_surf.get_width() - 20, 20))

        # Overlay messages
        if not self.started:
            self._draw_centered("DINO RUNNER", font_big, BLACK, HEIGHT // 2 - 50)
            self._draw_centered("Press SPACE or ↑ to start", font_med, DARK_GREY, HEIGHT // 2 + 10)
            self._draw_centered("↓ to duck", font_small, GREY, HEIGHT // 2 + 38)

        if self.game_over:
            self._draw_centered("GAME OVER", font_big, BLACK, HEIGHT // 2 - 40)
            self._draw_centered("Press SPACE or ↑ to restart", font_med, DARK_GREY, HEIGHT // 2 + 20)

        pygame.display.flip()

    def _draw_centered(self, text, font, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


# --- Main Loop ---
def main():
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not game.started:
                        game.started = True
                    elif game.game_over:
                        game.reset()
                        game.started = True
                    else:
                        game.dino.jump()
                if event.key == pygame.K_DOWN:
                    game.dino.duck(True)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    game.dino.duck(False)

        game.update()
        game.draw()
        clock.tick(FPS)


if __name__ == "__main__":
    main()