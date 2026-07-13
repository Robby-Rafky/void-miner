"""Void Miner — an asteroid mining game.

Current features:
  * A ship sitting in space.
  * Scan the surrounding void for a minable asteroid.
  * Fly to a found asteroid (travel takes a fixed amount of time for now).

Controls:
  S      Scan for an asteroid
  F      Fly to the found asteroid
  ESC/Q  Quit
"""

import math
import random

import pygame

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 960, 640
FPS = 60

TRAVEL_TIME = 10.0      # seconds to fly to an asteroid
SCAN_TIME = 1.5         # seconds a scan sweep takes
SCAN_RANGE = 420        # how far out the radar can reach (pixels)

# Colors
BLACK = (8, 10, 18)
WHITE = (235, 240, 255)
GREY = (120, 130, 150)
CYAN = (90, 220, 235)
AMBER = (240, 190, 90)
GREEN = (120, 235, 150)
ROCK = (140, 120, 105)
ROCK_DARK = (95, 80, 70)


# ---------------------------------------------------------------------------
# Game states
# ---------------------------------------------------------------------------
class State:
    IDLE = "idle"                 # sitting, nothing found
    SCANNING = "scanning"         # radar sweep running
    ASTEROID_FOUND = "found"      # asteroid located, waiting to fly
    TRAVELING = "traveling"       # flying to the asteroid
    ARRIVED = "arrived"           # docked at asteroid, ready to mine


class Asteroid:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = random.randint(22, 40)
        # a lumpy outline so it doesn't look like a plain circle
        self.shape = []
        points = random.randint(9, 13)
        for i in range(points):
            ang = (i / points) * math.tau
            r = self.radius * random.uniform(0.75, 1.15)
            self.shape.append((math.cos(ang) * r, math.sin(ang) * r))

    def draw(self, surf, center=None):
        cx, cy = center if center else self.pos
        pts = [(cx + x, cy + y) for x, y in self.shape]
        pygame.draw.polygon(surf, ROCK, pts)
        pygame.draw.polygon(surf, ROCK_DARK, pts, 2)


class Ship:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.angle = -math.pi / 2  # pointing up

    def draw(self, surf):
        # a simple triangle ship pointing along self.angle
        size = 16
        tip = self.pos + pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * size
        left = self.pos + pygame.Vector2(
            math.cos(self.angle + 2.5), math.sin(self.angle + 2.5)
        ) * size
        right = self.pos + pygame.Vector2(
            math.cos(self.angle - 2.5), math.sin(self.angle - 2.5)
        ) * size
        pygame.draw.polygon(surf, CYAN, [tip, left, right])
        pygame.draw.polygon(surf, WHITE, [tip, left, right], 1)


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Void Miner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 26, bold=True)

        self.ship = Ship((WIDTH / 2, HEIGHT / 2))
        self.state = State.IDLE
        self.asteroid = None

        # timers / progress
        self.scan_elapsed = 0.0
        self.travel_elapsed = 0.0
        self.travel_start = None  # ship position when travel began

        # starfield background
        self.stars = [
            (random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random())
            for _ in range(180)
        ]

        self.running = True

    # -- input --------------------------------------------------------------
    def handle_key(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif key == pygame.K_s:
            if self.state in (State.IDLE, State.ASTEROID_FOUND, State.ARRIVED):
                self.start_scan()
        elif key == pygame.K_f:
            if self.state == State.ASTEROID_FOUND:
                self.start_travel()

    # -- actions ------------------------------------------------------------
    def start_scan(self):
        self.state = State.SCANNING
        self.scan_elapsed = 0.0
        self.asteroid = None

    def finish_scan(self):
        # place an asteroid somewhere within scan range but not on top of ship
        angle = random.uniform(0, math.tau)
        dist = random.uniform(SCAN_RANGE * 0.4, SCAN_RANGE)
        pos = self.ship.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        pos.x = max(60, min(WIDTH - 60, pos.x))
        pos.y = max(90, min(HEIGHT - 60, pos.y))
        self.asteroid = Asteroid(pos)
        self.state = State.ASTEROID_FOUND

    def start_travel(self):
        self.state = State.TRAVELING
        self.travel_elapsed = 0.0
        self.travel_start = pygame.Vector2(self.ship.pos)
        # point the ship at the asteroid
        d = self.asteroid.pos - self.ship.pos
        self.ship.angle = math.atan2(d.y, d.x)

    # -- update -------------------------------------------------------------
    def update(self, dt):
        if self.state == State.SCANNING:
            self.scan_elapsed += dt
            if self.scan_elapsed >= SCAN_TIME:
                self.finish_scan()

        elif self.state == State.TRAVELING:
            self.travel_elapsed += dt
            t = min(self.travel_elapsed / TRAVEL_TIME, 1.0)
            # ease-in-out for a nicer glide
            eased = t * t * (3 - 2 * t)
            self.ship.pos = self.travel_start.lerp(self.asteroid.pos, eased)
            if t >= 1.0:
                self.state = State.ARRIVED

    # -- drawing ------------------------------------------------------------
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_stars()

        if self.state == State.SCANNING:
            self.draw_scan()

        if self.asteroid and self.state in (
            State.ASTEROID_FOUND,
            State.TRAVELING,
            State.ARRIVED,
        ):
            self.asteroid.draw(self.screen)
            # marker ring around a found asteroid
            if self.state == State.ASTEROID_FOUND:
                pygame.draw.circle(
                    self.screen, AMBER, self.asteroid.pos,
                    self.asteroid.radius + 12, 1
                )

        self.ship.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def draw_stars(self):
        for x, y, b in self.stars:
            shade = int(60 + b * 160)
            self.screen.set_at((x, y), (shade, shade, shade + 20))

    def draw_scan(self):
        t = self.scan_elapsed / SCAN_TIME
        radius = int(SCAN_RANGE * t)
        alpha = max(0, int(180 * (1 - t)))
        ring = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*CYAN, alpha), self.ship.pos, radius, 2)
        self.screen.blit(ring, (0, 0))

    def draw_hud(self):
        # top bar: status
        status = {
            State.IDLE: "Idle — press [S] to scan the void",
            State.SCANNING: "Scanning...",
            State.ASTEROID_FOUND: "Asteroid located! Press [F] to fly there",
            State.TRAVELING: "In transit...",
            State.ARRIVED: "Docked at asteroid — ready to mine",
        }[self.state]

        color = {
            State.IDLE: GREY,
            State.SCANNING: CYAN,
            State.ASTEROID_FOUND: AMBER,
            State.TRAVELING: CYAN,
            State.ARRIVED: GREEN,
        }[self.state]

        self.screen.blit(self.big_font.render(status, True, color), (20, 18))

        # travel progress bar
        if self.state == State.TRAVELING:
            t = min(self.travel_elapsed / TRAVEL_TIME, 1.0)
            remaining = max(0.0, TRAVEL_TIME - self.travel_elapsed)
            bar_w, bar_h = 300, 16
            bx, by = 20, 56
            pygame.draw.rect(self.screen, GREY, (bx, by, bar_w, bar_h), 1)
            pygame.draw.rect(self.screen, CYAN, (bx, by, int(bar_w * t), bar_h))
            self.screen.blit(
                self.font.render(f"ETA {remaining:4.1f}s", True, WHITE),
                (bx + bar_w + 12, by - 1),
            )

        # controls footer
        controls = "[S] Scan    [F] Fly    [Q] Quit"
        self.screen.blit(
            self.font.render(controls, True, GREY), (20, HEIGHT - 30)
        )

    # -- main loop ----------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
