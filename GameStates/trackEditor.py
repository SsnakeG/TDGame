from GameItems.objects import Button, PopupWindow, MapsPage
from GameItems.tdImages import undoImg, RedoImg, saveImg, trashImg, homeImg, popupBackground
from GameItems.tdColors import *
from pygame import QUIT, MOUSEBUTTONDOWN, SRCALPHA, Surface
from GameItems.AutoResizableNum import rNum

blockSize = rNum(20, 2)


class TrackEditor:
    def __init__(self, drawingSurface):
        self.undoBtn = Button(10, 505, undoImg, 0.3, 0.3)
        self.redoBtn = Button(110, 505, RedoImg, 0.3, 0.3)
        self.saveBtn = Button(400, 505, saveImg, 0.3, 0.3)
        self.trashBtn = Button(500, 505, trashImg, 0.3, 0.3)
        self.homeBtn = Button(255, 505, homeImg, 0.3, 0.3)

        self.permissionErrorPopup = PopupWindow(popupBackground,
                                           text='Your PC has blocked the application from saving the map!',
                                           optionNum=1)
        self.homeConfirmationPopup = PopupWindow(popupBackground, text='Are you sure you would like to leave to map editor?',
                                            scale=[.75, .75], textColor=DARK_BLUE)
        self.clearConfirmationPopup = PopupWindow(popupBackground,
                                             text='Are you sure you would like to clear the map editor?',
                                             scale=[.75, .75], textColor=DARK_BLUE)
        self.saveConfirmationPopup = PopupWindow(popupBackground,
                                            text='Are you sure you would like to save this custom map?',
                                            scale=[.75, .75], textColor=DARK_BLUE)
        self.surface = drawingSurface
        size = min(drawingSurface.get_size())
        self.mainSurface = Surface((size, size), SRCALPHA)

        self.newPathParts = []
        self.undoneList = []

        self.saveConfirmation = False
        self.homeConfirmation = False
        self.clearConfirmation = False
        self.permissionIssues = False

    def checkClicks(self, clicked, mousePos, blockArray):
        if not self.permissionIssues and not self.homeConfirmation and not self.clearConfirmation and not self.saveConfirmation:

            if self.homeBtn.check_click(clicked, mousePos):
                self.homeConfirmation = True
            if self.undoBtn.check_click(clicked, mousePos):
                try:
                    self.undoneList.append(self.newPathParts[-1])
                    undone = self.newPathParts.pop(-1)
                    self.resetBlockColor(undone, blockArray, reset=True)

                    for pathPart in self.newPathParts:
                        self.resetBlockColor(pathPart, blockArray)
                except IndexError:
                    pass

            if self.redoBtn.check_click(clicked, mousePos):
                try:
                    self.newPathParts.append(self.undoneList[-1])
                    redone = self.undoneList.pop(-1)
                    self.resetBlockColor(redone, blockArray)
                except IndexError:
                    pass

            if self.saveBtn.check_click(clicked, mousePos):
                self.saveConfirmation = True

            if self.trashBtn.check_click(clicked, mousePos):
                self.clearConfirmation = True

    def confirmation(self, clicked, mousePos, blockArray, clickAllowed, mapMenu):
        pathEditing = True
        mapSelector = False
        if self.homeConfirmation:
            self.homeConfirmationPopup.draw(self.surface)
            if self.homeConfirmationPopup.optionYes.check_click(clicked, mousePos, (self.homeConfirmationPopup.x, self.homeConfirmationPopup.y)):
                pathEditing = False
                mapSelector = True
                clickAllowed = False

                for part in self.newPathParts:
                    self.resetBlockColor(part, blockArray, reset=True)
                self.newPathParts = []
                self.homeConfirmation = False
            elif self.homeConfirmationPopup.optionNo.check_click(clicked, mousePos, (self.homeConfirmationPopup.x, self.homeConfirmationPopup.y)):
                self.homeConfirmation = False

        elif self.clearConfirmation and self.newPathParts:
            self.clearConfirmationPopup.draw(self.surface)
            if self.clearConfirmationPopup.optionYes.check_click(clicked, mousePos, (self.clearConfirmationPopup.x, self.clearConfirmationPopup.y)):
                for part in self.newPathParts:
                    self.resetBlockColor(part, blockArray, reset=True)
                self.newPathParts = []
                self.clearConfirmation = False
            elif self.clearConfirmationPopup.optionNo.check_click(clicked, mousePos, (self.clearConfirmationPopup.x, self.clearConfirmationPopup.y)):
                self.clearConfirmation = False

        elif self.saveConfirmation and self.newPathParts:
            self.saveConfirmationPopup.draw(self.surface)
            if self.saveConfirmationPopup.optionYes.check_click(clicked, mousePos, (self.saveConfirmationPopup.x, self.saveConfirmationPopup.y)):
                newPath = self.compileCustomPath(self.newPathParts)
                permissionIssues = self.save(newPath, mapMenu)
                self.saveConfirmation = False
                clickAllowed = False
                if not permissionIssues:
                    mapMenu.maps.append(newPath)
                    self.addNewMap(newPath, mapMenu)
            elif self.saveConfirmationPopup.optionNo.check_click(clicked, mousePos, (self.saveConfirmationPopup.x, self.saveConfirmationPopup.y)):
                self.saveConfirmation = False

        return clickAllowed, pathEditing, mapSelector

    def update(self, events, mousePos, blockArray):
        run = True
        for ev in events:
            if ev.type == QUIT:
                run = False
            if ev.type == MOUSEBUTTONDOWN:
                if ev.button == 1 and not self.saveConfirmation and not self.homeConfirmation and not self.clearConfirmation:
                    changeMade = self.makeCustomPathPart(mousePos, blockArray, BEIGE, self.newPathParts)
                    if changeMade:
                        self.undoneList = []
        self.draw(blockArray)
        return run

    def draw(self, blockArray):
        for layer in blockArray:
            for block in layer:
                block.draw(self.surface)

        self.redoBtn.draw(self.surface)
        self.undoBtn.draw(self.surface)
        self.saveBtn.draw(self.surface)
        self.trashBtn.draw(self.surface)
        self.homeBtn.draw(self.surface)

    @staticmethod
    def save(mp, mapMenu):
        map_str = ''
        map_strs = []
        for additionalMap in mapMenu.maps:
            if additionalMap != mp:
                if additionalMap:
                    for coord in additionalMap:
                        if map_str:
                            map_str += f'-{coord}'
                        else:
                            map_str += str(coord)
                    map_strs.append(map_str)
                    map_str = ''
        for coord in mp:
            if map_str:
                map_str += f'-{coord}'
            else:
                map_str += str(coord)
        map_strs.append(map_str)
        try:
            with open('maps.txt', 'w') as file:
                for map_str in map_strs:
                    file.write(f'{map_str}\n')
        except PermissionError:
            return True

    @staticmethod
    def compileCustomPath(pathParts):
        path = []
        for part in pathParts:
            for coord in part:
                path.append(coord)
        return path

    @staticmethod
    def addNewMap(mp, mapMenu):
        modifiedPage = MapsPage.pages[-1]
        for mapNumber, m in enumerate(modifiedPage.maps):
            if not m.map:
                modifiedPage.maps[mapNumber].map = mp
                return
        MapsPage(MapsPage.pages.index(modifiedPage) + 1, mp, None, None, None, None, None)
        mapMenu.pages += 1

    @staticmethod
    def resetBlockColor(blocks, blockArray, color=BEIGE, reset=False):
        if reset:
            for block in blocks:
                blockArray[block[1]][block[0]].color = blockArray[block[1]][block[0]].initialColor
        else:
            for block in blocks:
                blockArray[block[1]][block[0]].color = color

    @staticmethod
    def makeCustomPathPart(mousePos, blocks, pathColor, pathParts):
        newPathPart = []
        try:  # checks for an empty list
            blocks[int((mousePos[0]-rNum(50, 0).end()) / blockSize.get())][int((mousePos[1]-15) / blockSize.get())]
        except IndexError:
            return None
        square = (int((mousePos[0]-rNum(50, 0).end()) / blockSize.get()), int((mousePos[1]-15) / blockSize.get()))
        block = blocks[square[1]][square[0]]
        block.color = pathColor
        try:
            last_square = pathParts[len(pathParts) - 1][len(pathParts[len(pathParts) - 1]) - 1]
        except IndexError:
            newPathPart.append(square)
            pathParts.append(newPathPart)
            return True
        try:
            if square[0] != last_square[0] and square[1] != last_square[1]:
                block.color = block.initialColor
                return None
            elif square[0] == last_square[0]:  # same column
                if square[1] < last_square[1]:  # up
                    for iterable1 in range(1 + last_square[1] - square[1]):
                        new_square = (square[0], int(last_square[1] - iterable1))
                        new_block = blocks[new_square[1]][new_square[0]]
                        new_block.color = pathColor
                        newPathPart.append(new_square)
                elif square[1] > last_square[1]:  # down
                    for iterable2 in range(1 + square[1] - last_square[1]):
                        new_square = (square[0], int(last_square[1] + iterable2))
                        new_block = blocks[new_square[1]][new_square[0]]
                        new_block.color = pathColor
                        newPathPart.append(new_square)

            elif square[1] == last_square[1]:  # same row
                if square[0] < last_square[0]:  # left
                    for i in range(1 + last_square[0] - square[0]):
                        new_square = (last_square[0] - i, square[1])
                        new_block = blocks[new_square[1]][new_square[0]]
                        new_block.color = pathColor
                        newPathPart.append(new_square)
                elif square[0] > last_square[0]:  # right
                    for i in range(1 + square[0] - last_square[0]):
                        new_square = (last_square[0] + i, square[1])
                        new_block = blocks[new_square[1]][new_square[0]]
                        new_block.color = pathColor
                        newPathPart.append(new_square)
        except UnboundLocalError:
            pass
        pathParts.append(newPathPart[1:])
        return True
