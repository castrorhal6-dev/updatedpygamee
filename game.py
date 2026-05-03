import pygame
import sys

from lanes import Lanes
from character import Character
from background import Background
from obstacles import Obstacle
from gates import Gate

pygame.init()
pygame.mixer.init() 
pygame.display.set_caption("Run & Resolve!")


class Game:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.running = True

        self.state = "menu"
        self.paused = False
        self.difficulty = "Easy"

        self.tap_sound = pygame.mixer.Sound("tap.ogg")
        self.correct_sound = pygame.mixer.Sound("win.ogg")
        self.wrong_sound = pygame.mixer.Sound("lose.ogg")
        self.tap_sound.set_volume(0.5)
        self.correct_sound.set_volume(0.6)
        self.wrong_sound.set_volume(0.6)

        self.background = Background(800, 800)
        self.lanes = Lanes(self.WIDTH, self.HEIGHT)
        self.player = Character(self.lanes, self.HEIGHT)

        self.font = pygame.font.SysFont(None, 40)
        self.big_font = pygame.font.SysFont(None, 80)

        # GAME DATA
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_delay = 3
        self.meters = 0
        self.meter_speed = 60
        self.survival_time = 0

        # GATE SYSTEM
        self.gate = None
        self.last_gate_spawn = 0
        self.in_gate_mode = False

        # BUTTONS
        self.start_btn = pygame.Rect(220, 330, 360, 95)
        self.quit_btn = pygame.Rect(220, 450, 360, 95)

        self.easy_btn = pygame.Rect(220, 280, 360, 95)
        self.medium_btn = pygame.Rect(220, 400, 360, 95)
        self.hard_btn = pygame.Rect(220, 520, 360, 95)

        # LOAD IMAGES
        self.title_img = pygame.image.load("title.png").convert_alpha()
        self.start_img = pygame.image.load("start.png").convert_alpha()
        self.easy_img = pygame.image.load("easy.png").convert_alpha()
        self.medium_img = pygame.image.load("medium.png").convert_alpha()
        self.hard_img = pygame.image.load("hard.png").convert_alpha()
        self.quit_img = pygame.image.load("quit.png").convert_alpha()
        self.select_img = pygame.image.load("select_difficulty.png").convert_alpha()

        # SCALE
        self.title_img = pygame.transform.scale(self.title_img, (700, 200))
        self.start_img = pygame.transform.scale(self.start_img, (360, 95))
        self.easy_img = pygame.transform.scale(self.easy_img, (360, 95))
        self.medium_img = pygame.transform.scale(self.medium_img, (360, 95))
        self.hard_img = pygame.transform.scale(self.hard_img, (360, 95))
        self.quit_img = pygame.transform.scale(self.quit_img, (360, 95))
        self.select_img = pygame.transform.scale(self.select_img, (400, 80))

        self.title_rect = self.title_img.get_rect(center=(400, 150))

    def restart(self):
        self.obstacles.clear()
        self.meters = 0
        self.spawn_timer = 0
        self.player = Character(self.lanes, self.HEIGHT)

        self.state = "playing"
        self.paused = False

        self.gate = None
        self.last_gate_spawn = 0
        self.in_gate_mode = False

    def draw_text(self, text, x, y, big=False):
        font = self.big_font if big else self.font
        surface = font.render(text, True, (255, 255, 255))
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)

    def handle_events(self):
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.state == "playing":
                    self.paused = not self.paused

            if event.type == pygame.MOUSEBUTTONDOWN:

                # MENU
                if self.state == "menu":
                    if self.start_btn.collidepoint(mouse):
                        self.state = "difficulty"

                    elif self.quit_btn.collidepoint(mouse):
                        self.running = False

                # DIFFICULTY
                elif self.state == "difficulty":

                    if self.easy_btn.collidepoint(mouse):
                        self.difficulty = "Easy"
                        self.spawn_delay = 3
                        self.meter_speed = 50
                        self.restart()

                    elif self.medium_btn.collidepoint(mouse):
                        self.difficulty = "Medium"
                        self.spawn_delay = 2
                        self.meter_speed = 70
                        self.restart()

                    elif self.hard_btn.collidepoint(mouse):
                        self.difficulty = "Hard"
                        self.spawn_delay = 1
                        self.meter_speed = 90
                        self.restart()

                # GAME OVER
                elif self.state == "game_over":
                    self.state = "menu"

            # player controls stay active
            if self.state == "playing" and not self.paused:
                self.player.handle_input(event)

    def update(self, dt):
        if self.state != "playing" or self.paused:
            return

        self.player.update(dt)
        self.background.update()

        self.meters += self.meter_speed * dt
        self.survival_time += dt

        # SPAWN GATE EVERY 100m
        if self.gate is None and self.meters - self.last_gate_spawn >= 100:
            self.gate = Gate(self.difficulty)
            self.last_gate_spawn = self.meters
            self.in_gate_mode = True
            self.obstacles.clear()

        # ✅ ALWAYS UPDATE GATE IF IT EXISTS
        if self.gate is not None:
            self.gate.update(dt)

            # CHECK IF PLAYER REACHED GATE
            if self.gate.is_finished():
                result = self.gate.check_answer(self.player.lane)

                if result is True:
                    print("CORRECT")
                    self.correct_sound.stop()
                    self.correct_sound.play()

                    self.gate = None
                    self.in_gate_mode = False

                elif result is False:
                    print("WRONG")

                    self.wrong_sound.stop()   # prevents overlap (optional but good)
                    self.wrong_sound.play()   # 🎧 PLAY WRONG SOUND

                    self.state = "game_over"

        # STOP obstacles during gate mode
        if not self.in_gate_mode:
            self.spawn_timer += dt

            if self.spawn_timer >= self.spawn_delay:
                self.obstacles.append(
                    Obstacle(self.lanes, self.HEIGHT)
                )
                self.spawn_timer = 0

        # update obstacles
        for obs in self.obstacles:
            obs.update(dt)

        self.obstacles = [
            o for o in self.obstacles
            if not o.is_off_screen()
        ]

        # collision
        for obs in self.obstacles:
            if obs.y < 0:
                continue

            if self.player.hitbox.colliderect(obs.hitbox):

                if obs.type == "low" and not self.player.is_jumping:
                    self.state = "game_over"

                elif obs.type == "high" and self.player.state != "crouch":
                    self.state = "game_over"

    def draw(self):
        self.screen.fill((30, 30, 30))

        # MENU
        if self.state == "menu":
            self.background.draw(self.screen)

            self.screen.blit(self.title_img, self.title_rect)
            self.screen.blit(self.start_img, self.start_btn)
            self.screen.blit(self.quit_img, self.quit_btn)

        # DIFFICULTY
        elif self.state == "difficulty":
            self.background.draw(self.screen)

            self.screen.blit(self.select_img, (200, 120))
            self.screen.blit(self.easy_img, self.easy_btn)
            self.screen.blit(self.medium_img, self.medium_btn)
            self.screen.blit(self.hard_img, self.hard_btn)

        # GAME
        else:
            self.background.draw(self.screen)

            for obs in self.obstacles:
                obs.draw(self.screen)

            # draw gate
            if self.gate:
                self.gate.draw(self.screen)

            self.player.draw(self.screen)

            # METERS
            self.draw_text(f"{int(self.meters)} m", 70, 30)

            # TIMER
            minutes = int(self.survival_time // 60)
            seconds = int(self.survival_time % 60)
            self.draw_text(f"Time: {minutes:02}:{seconds:02}", 105, 70)

            # MODE
            self.draw_text(f"Mode: {self.difficulty}", 95, 110)

            # PAUSE
            self.draw_text("P = Pause", 85, 150)

            if self.paused:
                self.draw_text("PAUSED", 400, 350, True)

            if self.state == "game_over":
                self.draw_text("GAME OVER", 400, 330, True)
                self.draw_text("CLICK TO RETURN MENU", 400, 410)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


Game().run()
