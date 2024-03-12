from pygame import Surface, transform

from GameItems.GUI import NoImgButton, Button, MapsPage
from GameItems.tdImages import leftArrow, rightArrow, mapSelected
from GameItems.tdColors import *
from GameItems.autoResizableNum import rNum


class MapSelector:
    def __init__(self, drawingSurface: Surface, mainSurface: Surface):
        self.playButton = NoImgButton(305, 40, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Play Game", fontSize=30)
        self.newMapBtn = NoImgButton(15, 40, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Create Map", fontSize=30)
        self.menuButton = NoImgButton(160, 500, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Main Menu", fontSize=30)
        self.leftArrowBtn = Button(5, 255, leftArrow, 0.3, 0.3)
        self.rightArrowBtn = Button(505, 255, rightArrow, 0.3, 0.3)

        self.scale = (rNum(mapSelected.get_width(), 1), rNum(mapSelected.get_height(), 1))

        self.surface = drawingSurface
        self.mainSurface = mainSurface

        self.currentPage = None
        self.displayedMaps = None

        self.selectedMap = None
        self.chosenMap = None

        self.pageNumber = 0
        self.pages = None
        self.maps = self.loadMaps()
        self.newPage()

    def draw(self, mousePos, surfacePos):
        self.mainSurface.fill(EMPTY_COLOR)
        self.playButton.checkHovered(mousePos, surfacePos)
        self.newMapBtn.checkHovered(mousePos, surfacePos)
        self.menuButton.checkHovered(mousePos, surfacePos)

        self.playButton.draw(self.mainSurface)
        self.newMapBtn.draw(self.mainSurface)
        self.menuButton.draw(self.mainSurface)
        if self.pageNumber > 0:
            self.leftArrowBtn.draw(self.mainSurface)
        if self.pageNumber < self.pages - 1:
            self.rightArrowBtn.draw(self.mainSurface)

        for m in self.displayedMaps:
            for row in m.array:
                for mapBlock in row:
                    mapBlock.draw(self.mainSurface)
            if m.selected:
                self.mainSurface.blit(transform.scale(mapSelected, (self.scale[0].get(), self.scale[1].get())), (m.location[0].get(), m.location[1].get()))
        self.surface.blit(self.mainSurface, surfacePos)

    def loadMaps(self):
        maps = self.loadAll()
        numOfMaps = len(maps)
        self.pages = round(numOfMaps / 6 + 0.5)

        emptySpaces = 6 - numOfMaps % 6
        if emptySpaces == 6:
            self.pages -= 1

        if emptySpaces:
            for i in range(emptySpaces):
                maps.append(None)

        for i in range(self.pages):
            self.currentPage = MapsPage(i, maps[i * 6], maps[i * 6 + 1], maps[i * 6 + 2], maps[i * 6 + 3], maps[i * 6 + 4],
                            maps[i * 6 + 5])
        return maps

    def newPage(self):
        self.displayedMaps = MapsPage.pages[self.pageNumber].maps
        for i in range(6):
            self.displayedMaps[i].create_array()
            self.makePath(self.displayedMaps[i].map, self.displayedMaps[i].array, BEIGE)

    def checkClicks(self, clicked, mousePos, clickAllowed, loadOutMenu, surfacePos):
        mapSelector = True
        game = False
        menu = False
        pathEditing = False
        name = "No Tower Selected"
        win = False
        lose = False
        selectedUnit = None

        try:
            if clicked and clickAllowed:
                if self.playButton.checkClick():
                    loadOut = loadOutMenu.loadLoadOut()
                    game = True
                    mapSelector = False
                    self.chosenMap = self.maps[self.selectedMap.value]
                    selectedUnit = loadOut[0]
                    clickAllowed = False
                    win = False
                    lose = False
        except AttributeError:
            pass

        if clicked and clickAllowed and not pathEditing:
            if self.newMapBtn.checkClick():
                pathEditing = True
                mapSelector = False
                clickAllowed = False
                self.pageNumber = 0
                self.newPage()
                try:
                    self.selectedMap.selected = False
                    self.selectedMap = None
                except AttributeError:
                    pass
            elif self.menuButton.checkClick():
                clickAllowed = False
                mapSelector = False
                menu = True
                self.pageNumber = 0
                self.newPage()
                try:
                    self.selectedMap.selected = False
                    self.selectedMap = None
                except AttributeError:
                    pass

        if self.leftArrowBtn.check_click(clicked, mousePos) and self.pageNumber > 0 and clickAllowed and not pathEditing:
            self.pageNumber -= 1
            self.newPage()
            clickAllowed = False
            try:
                self.selectedMap.selected = False
                self.selectedMap = None
            except AttributeError:
                pass

        elif self.rightArrowBtn.check_click(clicked, mousePos) and self.pageNumber < self.pages - 1 and clickAllowed and not pathEditing:
            self.pageNumber += 1
            self.newPage()
            clickAllowed = False
            try:
                self.selectedMap.selected = False
                self.selectedMap = None
            except AttributeError:
                pass

        if clicked and clickAllowed and mapSelector:
            try:
                self.selectedMap.selected = False
            except AttributeError:
                pass
            try:
                self.selectedMap = MapsPage.pages[self.pageNumber].select(mousePos, surfacePos)
                self.selectedMap.selected = True
            except AttributeError:
                pass
            clickAllowed = False

        return mapSelector, game, name, win, lose, menu, pathEditing, selectedUnit, clickAllowed

    @staticmethod
    def loadAll() -> list:
        new_maps = []
        new_map = []
        with open('./GameItems/maps.txt', 'r') as file:
            loadedMaps = file.readlines()
            for loadedMap in loadedMaps:
                if loadedMap != '\n':
                    string_map = loadedMap.rstrip('\n')
                    string_map = string_map.split('-')
                    for coord in string_map:
                        coord = coord.replace('(', '')
                        coord = coord.replace(')', '')
                        new_coord = coord.split(', ')
                        new_map.append((int(new_coord[0]), int(new_coord[1])))
                    new_maps.append(new_map)
                    new_map = []
        return new_maps

    @staticmethod
    def makePath(path, blocks, path_color):
        if path:
            for square in path:
                newBlock = blocks[int(square[1])][int(square[0])]
                newBlock.color = path_color
                newBlock.is_path = True
