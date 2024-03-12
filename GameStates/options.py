from GameItems.GUI import NoImgButton, Slider, OptionBox
from GameItems.tdImages import *
from GameItems.tdColors import *
from pygame import Surface, SRCALPHA


class OptionMenu:
    def __init__(self, drawingSurface: Surface, mainSurface: Surface):
        self.menuButton = NoImgButton(160, 500, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Main Menu", fontSize=30)
        self.loadOutBtn = NoImgButton(160, 100, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Loadout", fontSize=30)
        self.rgbSlider = Slider(x=150, y=250, width=300, height=65, min=1, max=3, fillColor=[0, 0, 0], value=1)
        self.volumeSlider = Slider(x=150, y=400, width=300, height=65, max=1, interval=0.01, fillColor=RED, value=.5)

        self.surface = drawingSurface
        self.mainSurface = mainSurface

    def draw(self, mousePos, surfacePos):
        self.mainSurface.fill(EMPTY_COLOR)
        self.menuButton.checkHovered(mousePos, surfacePos)
        self.loadOutBtn.checkHovered(mousePos, surfacePos)

        self.menuButton.draw(self.mainSurface)
        self.loadOutBtn.draw(self.mainSurface)
        self.rgbSlider.draw(self.mainSurface)
        self.volumeSlider.draw(self.mainSurface)

        self.surface.blit(self.mainSurface, surfacePos)

    def updateSliders(self, surfacePos):
        self.rgbSlider.slide(surfacePos)
        self.volumeSlider.slide(surfacePos)

    def checkClicks(self, clicked, clickAllowed):
        options = True
        mainMenu = False
        loadOutSelector = False

        if clicked and clickAllowed:
            if self.menuButton.checkClick():
                options = False
                mainMenu = True
                clickAllowed = False

            if self.loadOutBtn.checkClick():
                loadOutSelector = True
                clickAllowed = False

        return options, mainMenu, loadOutSelector, clickAllowed


class LoadOutMenu:
    def __init__(self, drawingSurface: Surface, mainSurface: Surface):
        self.options = ["Scout", "Sniper", "Rifle", "Demolition", "Freezer", "Pyromaniac", "Minigunner", "Turret",
                        "Farm"]
        self.dictionary = {"Scout": scoutStats, "Sniper": sniper_stats, "Rifle": rifle_man_stats,
                           "Demolition": demoMan_stats,
                           "Freezer": freezer_stats,
                           "Pyromaniac": pyro_stats, "Minigunner": minigunner_stats, "Turret": turret_stats,
                           "Farm": farm_stats, "": scoutStats}

        self.optionsButton = NoImgButton(160, 500, 280, 90, DARK_BLUE, LIGHTER_BLUE, DARKER_CYAN, "Options",
                                         fontSize=30)

        self.loadOut1 = OptionBox(38, 100, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options)
        self.loadOut2 = OptionBox(310, 100, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options, selected=1)
        self.loadOut3 = OptionBox(38, 200, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options, selected=2)
        self.loadOut4 = OptionBox(310, 200, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options, selected=3)
        self.loadOut5 = OptionBox(38, 300, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options, selected=7)
        self.loadOut6 = OptionBox(310, 300, 252, 81, LIGHTER_BLUE, DARKER_CYAN, self.options, selected=6)

        self.s6, self.s5, self.s4, self.s3, self.s2, self.s1 = False, False, False, False, False, False
        self.alreadySelecting = False

        self.surface = drawingSurface
        self.mainSurface = mainSurface

    def draw(self, mousePos, surfacePos, clickAllowed, events, screenPos):
        self.mainSurface.fill(EMPTY_COLOR)
        self.optionsButton.checkHovered(mousePos, surfacePos)
        self.optionsButton.draw(self.mainSurface)
        self.updateLoadOut(clickAllowed, events, screenPos)
        self.surface.blit(self.mainSurface, surfacePos)

    def updateLoadOut(self, clickAllowed, events, surfacePos):
        self.s6 = self.selectLoadOutType(self.s6, self.loadOut6, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)
        self.s5 = self.selectLoadOutType(self.s5, self.loadOut5, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)
        self.s4 = self.selectLoadOutType(self.s4, self.loadOut4, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)
        self.s3 = self.selectLoadOutType(self.s3, self.loadOut3, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)
        self.s2 = self.selectLoadOutType(self.s2, self.loadOut2, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)
        self.s1 = self.selectLoadOutType(self.s1, self.loadOut1, self.mainSurface, self.alreadySelecting, clickAllowed,
                                         events, surfacePos)

        self.alreadySelecting = self.s1 or self.s2 or self.s3 or self.s4 or self.s5 or self.s6

    def checkClicks(self, clicked, clickAllowed):
        loadOutSelector = True

        if clicked and clickAllowed:
            if self.optionsButton.checkClick():
                loadOutSelector = False
                clickAllowed = False

        return loadOutSelector, clickAllowed

    def loadLoadOut(self):
        loadOut = [self.dictionary[self.options[self.loadOut1.selected]],
                   self.dictionary[self.options[self.loadOut2.selected]],
                   self.dictionary[self.options[self.loadOut3.selected]],
                   self.dictionary[self.options[self.loadOut4.selected]],
                   self.dictionary[self.options[self.loadOut5.selected]],
                   self.dictionary[self.options[self.loadOut6.selected]]]
        return loadOut

    @staticmethod
    def selectLoadOutType(sNum, loadOutNum, screen, alreadySelecting, clickAllowed, events, surfacePos):
        loadOutNum.draw(screen)
        if not alreadySelecting or sNum and clickAllowed:
            sNum = loadOutNum.update(events, surfacePos)
        return sNum
