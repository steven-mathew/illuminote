import pygame as pg
from renderer import GAME_RESOLUTION
import math
import random
from pygame.math import *
import utils
import sys


global particles
particles = []


global circle_effects
circle_effects = []

global sparks
sparks = []

global BULLET_IMAGE
BULLET_IMAGE = None

global cooldown
cooldown = 0

global LIGHT_IMAGE
LIGHT_IMAGE = pg.transform.scale(
    pg.image.load('resources/light.png'), (80, 80))


class Bullet(pg.sprite.Sprite):
    """ This class represents the bullet . """
    sound_pew = None
    sound_hit = None
    chan1 = None
    chan2 = None

    def __init__(self, angle, renderer, x, y, player, block_list):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = BULLET_IMAGE
        self.original_image = self.image

        self.angle = angle
        self.renderer = renderer

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.original_x = x
        self.original_y = y

        # self.bullet_shoot_sound()
        self.player = player
        self.block_list = block_list

        self.vx = math.cos(math.radians(self.angle)) * \
            3 * 3
        self.vy = math.sin(math.radians(self.angle)) * \
            3 * 3

    def bullet_shoot_sound(self):
        # chan1 = pg.mixer.find_channel()
        # if chan1:
        # chan1.set_volume(1.0, 0.0)
        # chan1.play(Bullet.sound_pew)

        # chan2 = pg.mixer.find_channel()
        # if chan2:
        # chan2.set_volume(
        # 0.0, 1.0)
        # chan2.play(Bullet.sound_pew)
        Bullet.sound_pew.play()

    def bullet_hit_sound(self):
        Bullet.sound_hit.play()

    def update(self):
        """ Move the bullet. """
        self.rect.x += self.vx
        self.rect.y -= self.vy

        w, h = self.original_image.get_size()

        if self.renderer.night:
            rot_img, rot_origin = self.renderer.rotate(
                self.original_image, (self.rect.x, self.rect.y), (w/2, h/2), self.angle)

            if utils.distance((self.rect.x, self.rect.y), (self.original_x, self.original_y)) > 20:
                self.renderer.filter.blit(
                    LIGHT_IMAGE, (self.rect.x - LIGHT_IMAGE.get_width() / 2, self.rect.y - LIGHT_IMAGE.get_height() / 2))

            self.renderer.base_surface.blit(rot_img, rot_origin)
        else:
            rot_img, rot_origin = self.renderer.rotate(
                self.original_image, (self.rect.x, self.rect.y), (w/2, h/2), self.angle)
            self.renderer.base_surface.blit(rot_img, rot_origin)

        for i, bullet in sorted(enumerate(self.player.bullet_list), reverse=True):
            down = bullet.rect.y > GAME_RESOLUTION[1]
            up = bullet.rect.y < 0
            right = bullet.rect.x > GAME_RESOLUTION[0]
            left = bullet.rect.x < 0

            if right or left or down or up:
                self.player.bullet_list.remove(bullet)
                self.renderer.all.remove(bullet)

                sign_x = 1 if left else -1 if right else 0
                sign_y = 1 if up else -1 if down else 0

                sparks.append([[bullet.rect.x + sign_x*15, bullet.rect.y + sign_y*15], random.randint(
                    0, 359), random.randint(7, 10) / 10, 5 * random.randint(5, 10) / 10, (241, 242, 218)])
                self.renderer.screen_shake = 4
                # self.bullet_hit_sound()
        for block in self.block_list:
            if self.rect.colliderect(block.rect):
                # self.vx *= -1
                # self.vy *= -1
                # sound
                # if self.rect.y + 3 >= block.rect.y or self.rect.y - 3 <= block.rect.y + block.h:
                # self.vy *= -1
                # if self.rect.x + 3 >= block.rect.x or self.rect.x - 3 <= block.rect.x + block.w:
                # self.vx *= -1

                # if block.rect.+y < self.rect.y or block.
                xd = (block.rect.x + block.w / 2) - \
                    (self.rect.x)  # this needs work
                yd = (block.rect.y + block.h / 2) - \
                    (self.rect.y)

                if xd < 0:
                    xd *= -1
                if yd < 0:
                    yd *= -1

                if xd > yd:
                    self.vx *= -1
                else:
                    self.vy *= -1

# this code is bad... don't look


class PlayerTwo(pg.sprite.Sprite):
    image_orig = pg.Surface([25, 25])
    image_orig.set_colorkey((0, 0, 0))
    image_orig.fill((241, 242, 218))

    image_orig2 = pg.Surface([25, 25])
    image_orig2.set_colorkey((0, 0, 0))
    image_orig2.fill((163, 206, 250))

    box_rand = [image_orig, image_orig2]

    def __init__(self, renderer, x, y, block_list, enemy=None):
        super(PlayerTwo, self).__init__()

        self.image = pg.image.load(
            'resources/player_animations/p2_idle/p2_idle_0.png').convert()
        global BULLET_IMAGE
        BULLET_IMAGE = pg.image.load('resources/p2_bullet.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.original_image = self.image

        self.rect = self.image.get_rect()
        self.renderer = renderer
        self.speed = 2
        self.position = Vector2(x, y)
        self.angle_speed = 0
        self.angle = 0
        self.accel = 0
        self.rot_accel = 0
        self.rot_max_speed = 7
        self.max_speed = 2.71828183  # for jokes
        self.dx = 0
        self.state = 'p2_idle'
        self.frame = 0

        # pg.mixer.pre_init(44100, -16, 10, 3072)
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.mixer.set_num_channels(32)

        Bullet.sound_pew = pg.mixer.Sound('resources/woosh3.wav')
        # Bullet.sound_hit = pg.mixer.Sound('resources/hit.wav')

        self.bullet_list = pg.sprite.Group()
        self.enemy = enemy

        self.health = 100
        self.block_list = block_list
        self.stun = 0

    def update(self):
        w, h = self.original_image.get_size()
        key_pressed = pg.key.get_pressed()

        global cooldown
        cooldown += self.renderer.clock.get_time()

        if cooldown > 115:
            cooldown = 0

        if self.stun > 0:
            self.stun -= 1

        if key_pressed[pg.K_a]:
            self.rot_accel = 1.5
        elif key_pressed[pg.K_d]:
            self.rot_accel = -1.5
        else:
            self.rot_accel = 0

        self.frame += 1
        if self.frame >= len(self.renderer.animation_database[self.state]):
            self.frame = 0
        player_img_id = self.renderer.animation_database[self.state][self.frame]
        player_img = self.renderer.animation_frames[player_img_id]

        rotated_image, origin = self.renderer.rotate(player_img,
                                                     self.position, (w/2, h/2), self.angle)

        if (self.health < 20):
            print('dead')
            sys.exit()
        else:
            rotated_image.fill((255, 255, 255, 2.55 * self.health),
                               None, pg.BLEND_RGBA_MULT)

        self.renderer.base_surface.blit(
            rotated_image, origin)

        for i, bullet in sorted(enumerate(self.enemy.bullet_list), reverse=True):
            if self.rect.colliderect(bullet.rect):
                self.enemy.bullet_list.remove(bullet)
                self.renderer.all.remove(bullet)

                circle_effects.append([[self.rect.x, self.rect.y], 15, [
                                      3, 0.2], [3, 0.3], (255, 255, 255)])
                sparks.append([[self.rect.x, self.rect.y], random.randint(
                    0, 359), random.randint(13, 18) / 10 * 1.5, 5 * random.randint(5, 10) / 10, (241, 242, 218)])
                self.renderer.screen_shake = 6
                self.health -= 5
        # Circle Effects ----------------------------------------- #
        # loc, radius, border_stats, speed_stats, color
        for i, circle in sorted(enumerate(circle_effects), reverse=True):
            circle[1] += circle[3][0]
            circle[2][0] -= circle[2][1]
            circle[3][0] -= circle[3][1]
            if circle[2][0] < 1:
                circle_effects.pop(i)
            else:
                pg.draw.circle(self.renderer.base_surface, circle[4], [int(circle[0][0]), int(
                    circle[0][1])], int(circle[1]), int(circle[2][0]))

        if key_pressed[pg.K_LSHIFT] and cooldown == 0:
            self.state, self.frame = self.renderer.change_state(
                self.state, self.frame, 'p2_shoot')

            px = self.position[0] + math.cos(math.radians(self.angle)) * 10
            py = self.position[1] - math.sin(math.radians(self.angle)) * 10

            image = pg.transform.rotate(
                random.choice(PlayerTwo.box_rand), random.randint(0, 360))
            rect = image.get_rect(center=(px, py))

            b = Bullet(self.angle, self.renderer,
                       self.position[0], self.position[1], self, self.block_list)
            self.bullet_list.add(b)
            self.renderer.add(b)

            self.renderer.base_surface.blit(image, rect)
            if self.renderer.night:
                self.renderer.filter.blit(
                    LIGHT_IMAGE, (self.position[0] - LIGHT_IMAGE.get_width() / 2, self.position[1] - LIGHT_IMAGE.get_height() / 2))
        else:
            self.state, self.frame = self.renderer.change_state(
                self.state, self.frame, 'p2_idle')

        # Sparks ------------------------------------------------- #
        for i, spark in sorted(enumerate(sparks), reverse=True):  # loc, dir, scale, speed
            speed = spark[3]
            scale = spark[2]
            points = [
                utils.advance(spark[0], spark[1], 2 * speed * scale),
                utils.advance(spark[0], spark[1] + 90, 0.3 * speed * scale),
                utils.advance(spark[0], spark[1], -1 * speed * scale),
                utils.advance(spark[0], spark[1] - 90, 0.3 * speed * scale),
            ]
            points = [[v[0], v[1]] for v in points]
            color = (241, 242, 218)
            # color = (255, 0,)
            if len(spark) > 4:
                color = spark[4]

            pg.draw.polygon(self.renderer.base_surface, color, points)

            spark[0] = utils.advance(spark[0], spark[1], speed)
            spark[3] -= 0.5
            if spark[3] <= 0:
                sparks.pop(i)

        # Handle acceleration
        if key_pressed[pg.K_w] and not self.stun:
            if self.accel_x == 0:
                self.accel_x = 0.7
        else:
            self.accel_x = 0

        for block in self.block_list:
            if self.rect.colliderect(block.rect):
                self.accel_x = -0.7
                self.stun = 45
                self.renderer.screen_shake = 2

        self.dx += self.accel_x

        if abs(self.dx) >= self.max_speed:
            self.dx = self.dx / abs(self.dx) * self.max_speed
        if self.accel_x == 0:
            self.dx *= 0.87

        newX = self.position[0] + math.cos(math.radians(self.angle)) * self.dx
        newY = self.position[1] - math.sin(math.radians(self.angle)) * self.dx

        self.position[0] = max(0, min(newX, GAME_RESOLUTION[0]))
        self.position[1] = max(0, min(newY, GAME_RESOLUTION[1]))

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        # Handle rotational interia
        self.angle_speed += self.rot_accel

        if abs(self.angle_speed) >= self.rot_max_speed:
            self.angle_speed = self.angle_speed / \
                abs(self.angle_speed) * self.rot_max_speed

        if self.rot_accel == 0:
            self.angle_speed *= 0.92

        self.angle += self.angle_speed
