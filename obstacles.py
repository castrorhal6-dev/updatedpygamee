import pygame
import random


class Obstacle:
    def __init__(self, lanes, height):
        self.lanes = lanes
        self.height = height

        self.lane = random.randint(0, 2)
        self.type = random.choice(["low", "high"])

        self.x = self.lanes.get_lane_x(self.lane)
        self.y = -150

        self.speed = 300

        # 👀 BIG VISIBLE SPRITES
        if self.type == "low":
            self.image = pygame.image.load("low_obstacle.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 100))
            self.hitbox = pygame.Rect(0, 0, 60, 60)
        else:
            self.image = pygame.image.load("high_obstacle.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (200, 200))
            self.hitbox = pygame.Rect(0, 0, 60, 90)

        # main sprite rect
        self.rect = self.image.get_rect(center=(self.x, self.y))
    def update(self, dt):
        self.y += self.speed * dt
        self.rect.center = (self.x, self.y)

    # set size ONCE per frame
        if self.type == "low":
            self.hitbox.size = (60, 60)
        else:
            self.hitbox.size = (60, 90)

    # stable positioning
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


    def is_off_screen(self):
        return self.y > self.height + 100