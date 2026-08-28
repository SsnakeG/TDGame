from pygame import draw
from GameItems.autoResizableNum import rNum
from GameItems.tdColors import BEIGE

class GameSquare:            # Autoresize check
    has_tower: bool
    block_list = []
    menu_block_list = []

    def __init__(self, location, color, size=64, not_main_game=False):
        self.location = tuple(map(lambda a: rNum(a, 2), location))
        self.color = color
        self.initialColor = color
        self.size = rNum(size, 2)
        self.is_path = False
        self.has_tower = False
        self.has_farm = False
        if not_main_game:
            GameSquare.menu_block_list.append(self)
        else:
            GameSquare.block_list.append(self)

    def changeColor(self, color=BEIGE, reset=False):
        if reset:
            self.color = self.initialColor
        else:
            self.color = color

    def draw(self, screen):
        draw.rect(screen, self.color, [self.location[0].get(), self.location[1].get(), int(self.size+1), int(self.size+1)], 0)