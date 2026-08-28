from GameItems.autoResizableNum import rNum
from GameItems.game_square import GameSquare


class Map:  # Autoresize check
    def __init__(self, mapList, location, value):
        self.map = mapList
        self.location = tuple(map(lambda a: rNum(a, 1), location))
        self.array: list[list[GameSquare]] = []
        self.value = value
        self.selected = False
        self.miniBlockSize = rNum(5, 1)

    def create_array(self):
        if self.array:
            self.array = []
        for i in range(24):
            self.array.append([])
            for j in range(24):
                block = GameSquare((self.location[0].initial() + j * self.miniBlockSize.initial(),
                               self.location[1].initial() + i * self.miniBlockSize.initial()), (0, 128, 0), 5, True)
                self.array[i].append(block)


class MapsPage:  # Autoresize check
    pages = []

    def __init__(self, number, map1, map2, map3, map4, map5, map6):
        self.number = number
        self.map1 = Map(map1, (100, 170), number * 6)
        self.map2 = Map(map2, (240, 170), number * 6 + 1)
        self.map3 = Map(map3, (380, 170), number * 6 + 2)
        self.map4 = Map(map4, (100, 320), number * 6 + 3)
        self.map5 = Map(map5, (240, 320), number * 6 + 4)
        self.map6 = Map(map6, (380, 320), number * 6 + 5)

        self.topRow = (rNum(170, 1), rNum(290, 1))
        self.bottomRow = (rNum(320, 1), rNum(440, 1))
        self.leftColumn = (rNum(100, 1), rNum(240, 1), rNum(380, 1))
        self.rightColumn = (rNum(220, 1), rNum(360, 1), rNum(500, 1))
        self.maps = [self.map1, self.map2, self.map3, self.map4, self.map5, self.map6]
        MapsPage.pages.append(self)

    def select(self, pos, offset=(0, 0)):
        selectedMap = None
        x = pos[0] - offset[0]
        y = pos[1] - offset[1]
        if self.topRow[0].get() < y < self.topRow[1].get():
            if self.leftColumn[0].get() < x < self.rightColumn[0].get():
                selectedMap = self.map1
            elif self.leftColumn[1].get() < x < self.rightColumn[1].get():
                selectedMap = self.map2
            elif self.leftColumn[2].get() < x < self.rightColumn[2].get():
                selectedMap = self.map3
        elif self.bottomRow[0].get() < y < self.bottomRow[1].get():
            if self.leftColumn[0].get() < x < self.rightColumn[0].get():
                selectedMap = self.map4
            elif self.leftColumn[1].get() < x < self.rightColumn[1].get():
                selectedMap = self.map5
            elif self.leftColumn[2].get() < x < self.rightColumn[2].get():
                selectedMap = self.map6
        return selectedMap