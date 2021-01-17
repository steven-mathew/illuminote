import pygame as pg
from renderer import Renderer
import sys
from player2 import PlayerTwo
from player import Player
from renderer import WINDOW_RESOLUTION
from block import Block
import random
import pygame_menu


class Game:
    """A game.
    """

    def __init__(self):
        """Initializes this game.
        """
        self.renderer = Renderer()
        self.renderer.draw()

    def set_up_blocks(self):
        """
        Set up the the map for the game
        """
        pass

    def run_game(self):
        """Run the game.
        """

        # block = Block(self.renderer, 200, 200, 150, 150, (0, 255, 0), 'wall')
        # block2 = Block(self.renderer, 500, 400, 150,
        # 150, (0, 0, 255), 'portal')
        # block3 = Block(self.renderer, 900, 400, 150,
        # 150, (0, 0, 255), 'portal')
        block_list = []
        btype = ['wall', 'portal']
        ctype = [(0, 255, 0), (0, 0, 255)]

        for _ in range(5):
            b = random.choice(btype)

            block_list.append(Block(self.renderer, random.randint(0, 1280), random.randint(
                0, 720), 150, 150, ctype[1] if b == 'portal' else ctype[0], b))

        player = Player(self.renderer, 36, 36, block_list)
        player2 = PlayerTwo(self.renderer, 72, 72, block_list, player)
        player.enemy = player2
        self.renderer.add(player)
        self.renderer.add(player2)

    # def __init__(self, renderer, x, y, w, h, color, block_type):
        for block in block_list:
            self.renderer.add(block)

        while True:
            # self.renderer.update()
            self.renderer.draw()
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.display.quit()
                    sys.exit()
                if e.type == pg.MOUSEBUTTONDOWN:
                    if self.renderer.night:
                        self.renderer.zap.play()
                    self.renderer.night = not self.renderer.night
                    self.renderer.bbu = 0
                    self.renderer.bbr = 0
                    self.renderer.bbd = 0
                    self.renderer.bbl = 0
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_f:
                        self.renderer.fullscreen = not self.renderer.fullscreen
                        if self.renderer.fullscreen:
                            self.renderer.window = pg.display.set_mode(
                                WINDOW_RESOLUTION, pg.FULLSCREEN, 32)
                        else:
                            self.renderer.window = pg.display.set_mode(
                                WINDOW_RESOLUTION, 0, 32)

            pg.display.update()


if __name__ == '__main__':
    game = Game()
    # game.run_game()

    mytheme = pygame_menu.themes.THEME_DARK.copy()
    mytheme.widget_font = pygame_menu.font.FONT_OPEN_SANS_BOLD
    mytheme.title_font = pygame_menu.font.FONT_OPEN_SANS_BOLD
    mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
    # Theme(widget_font=pygame_menu.font.FONT_NEVIS,
                              # title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_SIMPLE)
    mytheme.title_offset = (100, 0)
    menu = pygame_menu.Menu(300, 400, 'illuminote',
                            theme=mytheme)

    # menu.add_text_input('Name :', default='John Doe')
    # menu.add_selector(
    # 'Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
    menu.add_button('Play', game.run_game)
    menu.add_button('Change map', game.set_up_blocks)
    menu.add_button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(game.renderer.window)
