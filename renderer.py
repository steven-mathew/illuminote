import pygame as pg
import sys
import os
from pygame.math import *
import random
import utils


# GAME_RESOLUTION = (768, 432)
GAME_RESOLUTION = (1280, 720)
UPSCALE_FACTOR = 1
FPS = 60

WINDOW_RESOLUTION = (GAME_RESOLUTION[0]*UPSCALE_FACTOR + 64,
                     GAME_RESOLUTION[1]*UPSCALE_FACTOR + 36)


BACKGROUND_COLOR = (13, 20, 33)


global sparks
sparks = []

global LIGHT_OFF_SOUND
LIGHT_OFF_SOUND = None

global BUZZ_SOUND
BUZZ_SOUND = None


class Renderer:
    """
    Handles drawing and context operations
    """

    def __init__(self):
        """Initalizes renderer."""

        pg.init()

        self.window = pg.display.set_mode(WINDOW_RESOLUTION, 0, 32)
        self.clock = pg.time.Clock()

        self.base_surface = pg.Surface(GAME_RESOLUTION)
        self.all = pg.sprite.RenderUpdates()

        self.animation_frames = {}
        self.animation_database = {}
        self.animation_database['p1_idle'] = self.load_animations(
            'resources/player_animations/p1_idle', [1])
        self.animation_database['p1_shoot'] = self.load_animations(
            'resources/player_animations/p1_shoot', [3])

        self.animation_database['p2_idle'] = self.load_animations(
            'resources/player_animations/p2_idle', [1])
        self.animation_database['p2_shoot'] = self.load_animations(
            'resources/player_animations/p2_shoot', [3])
        self.night = False
        self.screen_shake = 0

        self.bbr = 0
        self.bbd = 0
        self.bbl = 0
        self.bbu = 0

        self.filter = pg.Surface(WINDOW_RESOLUTION)
        self.fullscreen = False

        self.flicker_cooldown = 0
        self.is_flickering = False

        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.mixer.set_num_channels(32)

        global LIGHT_OFF_SOUND
        LIGHT_OFF_SOUND = pg.mixer.Sound('resources/light_off2.wav')

        global BUZZ_SOUND
        BUZZ_SOUND = pg.mixer.Sound('resources/buzzz.mp3')
        self.can_light_off_sound = True

        pg.mixer.music.load('resources/buzzz.mp3')
        pg.mixer.music.set_volume(0.015)
        pg.mixer.music.play(-1, 0.0)

    def add(self, obj):
        self.all.add(obj)

    def circle_surf(self, radius, color):
        surf = pg.Surface((radius * 2, radius * 2))
        pg.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def render_flicker(self):
        # print('sdjlfhs')
        black_surf = pg.Surface(self.window.get_size())
        black_surf.fill((255, 0, 0))
        self.window.blit(black_surf, (0, 0))

    def render_border(self):
        if self.bbu < GAME_RESOLUTION[0]:
            self.bbu += 3
            sparks.append([[self.bbu, 0], random.randint(
                90, 180), random.randint(7, 10) / 15, 4 * random.randint(5, 10) / 10, (241, 242, 218)])

        if self.bbu >= GAME_RESOLUTION[0] and self.bbr < GAME_RESOLUTION[1]:
            self.bbr += 3
            sparks.append([[GAME_RESOLUTION[0], self.bbr], random.randint(
                180, 270), random.randint(7, 10) / 15, 4 * random.randint(5, 10) / 10, (241, 242, 218)])

        if self.bbr >= GAME_RESOLUTION[1] and self.bbd < GAME_RESOLUTION[0]:
            self.bbd += 3
            sparks.append([[GAME_RESOLUTION[0] - self.bbd, GAME_RESOLUTION[1]], random.randint(
                270, 359), random.randint(7, 10) / 15, 4 * random.randint(5, 10) / 10, (241, 242, 218)])

        if self.bbd >= GAME_RESOLUTION[0] and self.bbl < GAME_RESOLUTION[1]:
            self.bbl += 3
            sparks.append([[0, GAME_RESOLUTION[1] - self.bbl], random.randint(
                0, 90), random.randint(7, 10) / 15, 4 * random.randint(5, 10) / 10, (241, 242, 218)])

        if self.bbl >= GAME_RESOLUTION[1] and not self.is_flickering:
            # self.flicker_cooldown = 3
            # self.is_flickering = True
            # self.render_flicker()
            self.night = True

        if self.bbl >= 550:
            if self.can_light_off_sound:
                channel = pg.mixer.find_channel()
                channel.play(LIGHT_OFF_SOUND)
                self.can_light_off_sound = False

                # chan1 = pg.mixer.find_channel()
        # if chan1:
        # chan1.set_volume(1.0, 0.0)
        # chan1.play(Bullet.sound_pew)

        # chan2 = pg.mixer.find_channel()
        # if chan2:
        # chan2.set_volume(
        # 0.0, 1.0)
        # chan2.play(Bullet.sound_pew)

        border_box_right = pg.Rect(0, 0, 2, self.bbr)
        border_box_right.x = self.base_surface.get_width() - 2
        pg.draw.rect(self.base_surface, (241, 242, 218), border_box_right)

        border_box_down = pg.Rect(
            self.base_surface.get_width() - self.bbd, 0, self.bbd, 2)
        border_box_down.y = self.base_surface.get_height() - 2
        pg.draw.rect(self.base_surface, (241, 242, 218), border_box_down)

        border_box_left = pg.Rect(
            0, self.base_surface.get_height() - self.bbl, 2, self.bbl)
        pg.draw.rect(self.base_surface, (241, 242, 218), border_box_left)

        border_box_up = pg.Rect(0, 0, self.bbu, 2)
        pg.draw.rect(self.base_surface, (241, 242, 218), border_box_up)

        # Sparks ------------------------------------------------- #
        # loc, dir, scale, speed
        for i, spark in sorted(enumerate(sparks), reverse=True):
            speed = spark[3]
            scale = spark[2]
            points = [
                utils.advance(spark[0], spark[1], 2 * speed * scale),
                utils.advance(spark[0], spark[1] + 90,
                              0.3 * speed * scale),
                utils.advance(spark[0], spark[1], -1 * speed * scale),
                utils.advance(spark[0], spark[1] - 90,
                              0.3 * speed * scale),
            ]
            points = [[v[0], v[1]] for v in points]
            color = (241, 242, 218)
            # color = (255, 0,)
            if len(spark) > 4:
                color = spark[4]
            pg.draw.polygon(self.base_surface, color, points)
            spark[0] = utils.advance(spark[0], spark[1], speed)
            spark[3] -= 0.5
            if spark[3] <= 0:
                sparks.pop(i)

    def draw(self):
        self.clock.tick(FPS)
        self.base_surface.fill(BACKGROUND_COLOR)

        if self.screen_shake > 0:
            self.screen_shake -= 1

        if self.night:
            self.filter.fill((0, 0, 0))
            self.all.update()

            self.base_surface.blit(
                self.filter, (0, 0), special_flags=pg.BLEND_MULT
            )

            pg.mixer.music.set_volume(0.0)

        else:
            self.all.update()
            # self.render_border()
            # channel = pg.mixer.find_channel()
            # channel.play(BUZZ_SOUND)
            pg.mixer.music.set_volume(0.015)
        # print(self.flicker_cooldown)

        if self.flicker_cooldown > 0:
            self.flicker_cooldown -= 1
        else:
            display_background = self.base_surface.copy()
            display_background.set_alpha(45)  # background opacity
            black_surf = pg.Surface(self.window.get_size())
            black_surf.fill(BACKGROUND_COLOR)
            black_surf.set_alpha(125)  # blur
            self.base_surface.set_colorkey((BACKGROUND_COLOR))
            self.window.blit(pg.transform.scale(display_background,
                                                tuple(map(sum, zip(WINDOW_RESOLUTION, (10, 10))))), (-8, 0))
            self.window.blit(black_surf, (0, 0))
            offset = [0, 0]

            if self.screen_shake:
                offset[0] += random.randint(0, 10) - 5
                offset[1] += random.randint(0, 10) - 5
            self.window.blit(pg.transform.scale(self.base_surface,
                                                WINDOW_RESOLUTION), (offset[0], offset[1]))

        pg.display.flip()

    def rotate(self, player_img, pos, origin_pos, angle):
        """Rotate the image of the sprite around a pivot point."""

        # See https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
        w, h = player_img.get_size()
        box = [pg.math.Vector2(p)
               for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[
            0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[
            0], max(box_rotate, key=lambda p: p[1])[1])

        # Calculate the translation of the pivot
        pivot = pg.math.Vector2(origin_pos[0], -origin_pos[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot

        # Calculate the upper left origin of the rotated image
        origin = (pos[0] - origin_pos[0] + min_box[0] - pivot_move[0],
                  pos[1] - origin_pos[1] - max_box[1] + pivot_move[1])

        # Get a rotated image
        rotated_image = pg.transform.rotate(player_img, angle)
        rotated_image.set_colorkey((0, 0, 0))

        return rotated_image, origin

    def load_animations(self, path, frame_durations):
        # See https://www.youtube.com/watch?v=l-GUfEJcTH4&ab_channel=DaFluffyPotato

        animation_name = path.split('/')[-1]
        animation_frame_data = []
        n = 0
        for duration in frame_durations:
            animation_frame_id = animation_name + "_" + str(n)
            # print(path)
            img_loc = path + '/' + animation_frame_id + '.png'
            animation_image = pg.image.load(img_loc).convert()
            # animation_image = pg.transform.scale(animation_image, ())
            animation_image.set_colorkey((0, 0, 0))
            animation_image.set_alpha(255)
            self.animation_frames[animation_frame_id] = animation_image.copy()

            for i in range(duration):
                animation_frame_data.append(animation_frame_id)

            n += 1

        return animation_frame_data

    def change_state(self, action_var, frame, new_value):
        if action_var != new_value and frame == 0:
            action_var = new_value

        return action_var, frame
