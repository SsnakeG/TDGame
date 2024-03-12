from GameItems.GUI import PopupWindow, NoImgButton
from GameItems.tdImages import popupBackground
from GameItems.tdColors import *
from pygame import Surface


class Menu:
    def __init__(self, drawingSurface: Surface, mainSurface):
        self.playButton = NoImgButton(160, 150, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Play", fontSize=30)
        self.optionsButton = NoImgButton(160, 250, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Options", fontSize=30)
        self.quitButton = NoImgButton(160, 350, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Quit", fontSize=30)
        self.confirmClose = PopupWindow(popupBackground, text='Are you sure you want to quit the game?', scale=[.75, .75],
                           textColor=DARK_BLUE)

        self.quitting = False
        self.surface = drawingSurface
        self.mainSurface = mainSurface

    def draw(self, mousePos, surfacePos):
        self.mainSurface.fill(EMPTY_COLOR)
        if not self.quitting:
            self.playButton.checkHovered(mousePos, surfacePos)
            self.optionsButton.checkHovered(mousePos, surfacePos)
            self.quitButton.checkHovered(mousePos, surfacePos)
        self.playButton.draw(self.mainSurface)
        self.optionsButton.draw(self.mainSurface)
        self.quitButton.draw(self.mainSurface)
        if self.quitting:
            self.confirmClose.draw(self.mainSurface)
        self.surface.blit(self.mainSurface, surfacePos)

    def checkClicks(self, run, clicked, mousePos, clickAllowed, surfacePos):
        mainMenu = True
        options = False
        mapSelector = False

        if clicked and clickAllowed and not self.quitting:
            if self.playButton.checkClick():
                mainMenu = False
                mapSelector = True
                clickAllowed = False

            elif self.optionsButton.checkClick():
                mainMenu = False
                options = True
                clickAllowed = False

            elif self.quitButton.checkClick():
                self.quitting = True
                clickAllowed = False

        if self.quitting:
            run, clickAllowed = self.checkQuit(clicked, clickAllowed, mousePos, surfacePos)

        return mainMenu, options, run, mapSelector, clickAllowed

    def checkQuit(self, clicked, clickAllowed, mousePos, surfacePos):
        run = True

        if self.confirmClose.optionYes.check_click(clicked, mousePos, (self.confirmClose.x + surfacePos[0], self.confirmClose.y + surfacePos[1])) and clickAllowed:
            run = False
        elif self.confirmClose.optionNo.check_click(clicked, mousePos, (self.confirmClose.x + surfacePos[0], self.confirmClose.y + surfacePos[1])) and clickAllowed:
            self.quitting = False
            clickAllowed = False
            self.mainSurface.fill(EMPTY_COLOR)

        return run, clickAllowed
