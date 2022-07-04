import random
import math
import sys
import time

import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

class Game:

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsansms", 30)

        self.exit_game = False
        self.game_over = False

    def random_pipes(self):
        """ For generating random pipes one is upper and one is lower """

        pipe_height = self.game_sprites['pipe'][0].get_height()
        pipe_gap = 120
        min_upper_pipe, max_upper_pipe = 50, 180

        y1 = random.randint(min_upper_pipe, max_upper_pipe) - pipe_height
        y2 = y1 + pipe_height + pipe_gap
        return (y1, y2)

    def change_score(self, score):
        """ Increasing score bird passes pipe with out collision """

        txt = self.font.render(str(score), True, (255, 255, 255))
        self.window.blit(txt, [((self.screen_width / 2) - 10), 40])

    def changing_bird_image(self):
        """ This will change the bird image until the game stop """

        self.change_time += 1
        if self.change_time == self.change_bird_image_time:
            self.bird_image_no = 0 if self.bird_image_no == 1 else 1
            self.change_time = 0

        while True:
            yield pygame.transform.scale(self.game_sprites['bird'][self.bird_image_no], (45, 35))

    def moving_ground(self):
        """ Moving ground until the game stop """

        for index, i in enumerate(self.game_sprites['ground']):
            if index == 1:
                self.window.blit(self.game_sprites['ground'][1], (self.ground_2, self.ground))
            else:
                self.window.blit(self.game_sprites['ground'][0], (self.ground_1, self.ground))

        if self.ground_1 == -self.screen_width:
            self.game_sprites['ground'].append(pygame.image.load("Images/ground.png").convert_alpha())
            del self.game_sprites['ground'][0]

            self.ground_1 = 0
            self.ground_2 = self.screen_width

    def isCollideWithGround(self):
        """ Checking wheather the bird is collide with ground or not """
        bird_height = 35
        accurate_ground = self.ground - bird_height + 5

        if self.player_y > accurate_ground:
            self.game_sounds['die'].play()
            self.game_over = True

    def isCollideWithPipe(self, upper_pipe_position):
        """ Checking wheather the bird is collide with pipe or not """

        pipe_height = self.game_sprites['pipe'][0].get_height()
        pip_gap = 120

        point1 = upper_pipe_position + pipe_height
        point2 = point1 + pip_gap

        if self.player_y < point1 or (self.player_y + 35) > point2:
            self.game_sounds['hit'].play()
            self.game_over = True

    def open_window(self):
        self.screen_width = 312
        self.screen_height = 512

        self.window = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Flappy Bird Game")
        icon = pygame.image.load("Images/bird.png").convert_alpha()
        pygame.display.set_icon(icon)

        # Making dictionary of game sprites using comprehensions
        images_name = ["msg.png", "background.png", "gameover.png"]
        self.game_sprites = {f"{i[:len(i)-4]}" : pygame.image.load(f"Images/{i}").convert_alpha() for i in images_name}
        self.game_sprites['ground'] = [pygame.image.load("Images/ground.png").convert_alpha() for i in range(2)]
        self.game_sprites['bird'] = [
            pygame.image.load("Images/bird.png").convert_alpha(),
            pygame.image.load("Images/moving-bird.png").convert_alpha()
        ]
        self.game_sprites['pipe'] = [
            pygame.image.load("Images/pipe.png").convert_alpha(),
            pygame.transform.rotate(pygame.image.load("Images/pipe.png").convert_alpha(), 180) # Rotating image
        ]

        # Making dictionary of game sound effects using comprehensions
        game_sounds_name = ["die.wav", "hit.wav", "point.wav", "wing.wav"]
        self.game_sounds = {f"{i[:len(i)-4]}" : pygame.mixer.Sound(f"Audios/{i}") for i in game_sounds_name}

        # For changing bird action
        self.change_bird_image_time = 4
        self.bird_image_no = 0
        self.change_time = 0

        self.ground = 370 # Ground of the game

    def welcome_screen(self, fps):
        """ fps -> int -> frame per second """
        self.exit_game = False
        self.game_over = False
        self.player_x = (self.screen_width / 4)
        self.player_y = (self.screen_height / 3)

        while not self.exit_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.gameloop(32)

                else:
                    self.window.blit(pygame.transform.scale(
                        self.game_sprites['background'], (self.screen_width, self.screen_height)), (0, 0))
                    self.window.blit(pygame.transform.scale(
                        self.game_sprites['bird'][0], (45, 35)), (self.player_x, self.player_y))
                    self.window.blit(self.game_sprites['ground'][0], (0, self.ground))
                    self.window.blit(pygame.transform.scale(
                        self.game_sprites['msg'], (self.screen_width, self.screen_height)), (0, 0))
                    pygame.display.update()
                    self.clock.tick(fps)

    def gameloop(self, fps):
        """ Running game engine """
        self.exit_game = False
        self.game_over = False

        self.once = True
        score = 0
        gravity = 4
        flapped = False
        flapping_time = 0
        rotate_bird = 0
        self.ground_1 = 0
        pipe_width = self.game_sprites['pipe'][0].get_width()
        self.ground_2 = self.screen_width

        pipes = [
            {"x" : 310 + 200, "y" : self.random_pipes()},
            {"x" : 310 + 370, "y" : self.random_pipes()}
        ]
        pipe_velocity = -4

        self.change_score(0)

        while not self.exit_game:
            if not self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.exit_game = True
                        sys.exit()

                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                        if not flapped:
                            self.game_sounds['wing'].play()
                            flapped = True
                            gravity += -10

                self.window.fill((0, 0, 0))
                self.window.blit(pygame.transform.scale(self.game_sprites['background'], (310, 512)), (0, 0))
                bird = self.changing_bird_image().__next__()
                self.window.blit(bird, (self.player_x, self.player_y))

                # Bliting pipes
                for pipe in pipes:
                    for index, i in enumerate(self.game_sprites['pipe']):
                        self.window.blit(i, (pipe['x'], pipe['y'][index]))

                # Moving grounds
                self.ground_1 += -4
                self.ground_2 += -4
                self.moving_ground()

                # Generating new pipes
                if pipes[0]['x'] < 140 and self.once == True:
                    pipes.append({"x": pipes[1]['x'] + 170, "y": self.random_pipes()})
                    self.once = False

                # Removing pipe when it gone on left
                if pipes[0]['x'] < -50:
                    del pipes[0]
                    self.once = True

                # Moving pipes from right to left
                for i in pipes:
                    i['x'] += pipe_velocity

                # Increasing score
                if pipes[0]['x'] < self.player_x and self.once == False:
                    self.once = None # Giving the value none so once can be used in two conditions
                    self.game_sounds['point'].play()
                    score += 1

                # If bird is collide with pipe ? Answer =
                if pipes[0]['x'] < self.player_x and pipes[0]['x'] > (self.player_x - pipe_width):
                    upper_pipe = pipes[0]['y'][0]
                    self.isCollideWithPipe(upper_pipe)

                # Is collide with ground ? Answer =
                self.isCollideWithGround()

                # Controlling the flaping of bird
                if flapped == True:
                    flapping_time += 1

                if flapping_time > 10:
                    flapped = False
                    gravity = 4
                    flapping_time = 0

                self.player_y += gravity
                self.change_score(score)
                pygame.display.update()
                self.clock.tick(fps)

            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.exit_game = True
                        sys.exit()

                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                        self.welcome_screen(32)

                time.sleep(1)
                self.window.blit(self.game_sprites['gameover'], (0, 0))
                pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.open_window()
    game.welcome_screen(32)