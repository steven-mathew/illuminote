import pygame as pg


class Block(pg.sprite.Sprite):
    """
    Nearly square obstacles on the screen
    """

    def __init__(self, renderer, x, y, w, h, color, block_type):
        super(Block, self).__init__()

        self.image = pg.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.w = w
        self.h = h
        self.color = color
        self.block_type = block_type
        self.renderer = renderer

    def update(self):
        self.renderer.base_surface.blit(
            self.image, self.rect)
