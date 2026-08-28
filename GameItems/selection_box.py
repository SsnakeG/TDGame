

from GameItems.autoResizableNum import rNum, rNums, AutoResizableNum, AutoResizableSet
from pygame import Surface, draw, font
from GameItems.tdColors import DARK_BLUE, OPAQUE_LIGHT_BLUE, LIME_GREEN, LIME_GREEN2, DARKER_YELLOW, YELLOW, RED, PINK, WHITE
from GameItems.buttons import NoImgButton
from GameItems.tower import Tower
from GameItems.farm import Farm

class SelectionBox:
    def __init__(self):
        self.maxLevel = False
        self.fontSize = rNum(18, 1)
        self.width = rNum(250, 1)
        self.height = rNum(240, 1)
        self.surface = Surface((self.width.get(), self.height.get()))

        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))

        self.x = 0
        self.y = 0

        self.decals: list[AutoResizableSet] = [rNums(10, 10, 230, 220, intList=1), rNums(5, 35, 240, 5, intList=1)]
        self.textPos: list[AutoResizableSet] = [rNums(10, 10, intList=1), rNums(10, 40, intList=1),
                                                rNums(10, 60, intList=1), rNums(10, 80, intList=1)]

        self.upgradeButton = NoImgButton(10, 117, 170, 35, LIME_GREEN, LIME_GREEN, LIME_GREEN2, f"", fontSize=18,
                                         textColor=WHITE)
        self.targetButton = NoImgButton(10, 155, 170, 35, DARKER_YELLOW, DARKER_YELLOW, YELLOW, f"", fontSize=18,
                                        textColor=WHITE)
        self.sellButton = NoImgButton(10, 193, 170, 35, RED, RED, PINK, f"", fontSize=18, textColor=WHITE)

    def updateTowerButtons(self, selectedTower: Tower):
        try:
            self.maxLevel = False
            self.sellButton.update(f"Sell:    ${selectedTower.sell_price}")
            self.targetButton.update(f"Targeting: {Tower.targetOptions[selectedTower.targeting]}")
            self.upgradeButton.update(
                f"Upgrade: ${selectedTower.upgrades[selectedTower.level][3]}")
        except IndexError:
            self.maxLevel = True

    def updateFarmButtons(self, selectedFarm: Farm):
        try:
            self.sellButton.update(f"Sell:    ${selectedFarm.sell_price}")
            self.upgradeButton.update(f"Upgrade: ${selectedFarm.upgrades[selectedFarm.level][1]}")
        except IndexError:
            self.maxLevel = True

    def renderTowerText(self, selectedTower: Tower):
        nText = self.font.render(f"{selectedTower.type} lvl: {selectedTower.level}", True, DARK_BLUE)
        if selectedTower.level < 4:
            dText = self.font.render(
                f"Damage: {selectedTower.damage} >>> {selectedTower.damage + selectedTower.upgrades[selectedTower.level][1]}",
                True, DARK_BLUE)
            sText = self.font.render(
                f"Speed:  {selectedTower.speed:.2f} >>> {selectedTower.speed - selectedTower.upgrades[selectedTower.level][2]:.2f}",
                True, DARK_BLUE)
            rText = self.font.render(
                f"Range:  {selectedTower.range} >>> {selectedTower.range + selectedTower.upgrades[selectedTower.level][0]}",
                True, DARK_BLUE)
        else:
            dText = self.font.render(f"Damage: {selectedTower.damage}", True, DARK_BLUE)
            sText = self.font.render(f"Speed:  {selectedTower.speed:.2f}", True, DARK_BLUE)
            rText = self.font.render(f"Range:  {selectedTower.range}", True, DARK_BLUE)
        return nText, dText, sText, rText

    def renderFarmText(self, selectedTower: Farm):
        nText = self.font.render(f"{selectedTower.type} lvl: {selectedTower.level}", True, DARK_BLUE)
        if selectedTower.level < 4:
            mText = self.font.render(
                f"Money: ${selectedTower.moneyGain} >>> ${selectedTower.upgrades[selectedTower.level][0]}",
                True, DARK_BLUE)
        else:
            mText = self.font.render(f"Money: ${selectedTower.moneyGain}", True, DARK_BLUE)
        return nText, mText

    def draw(self, surface: Surface, selectedTower):
        try:
            self.surface.fill(DARK_BLUE)
            draw.rect(self.surface, OPAQUE_LIGHT_BLUE, self.decals[0].get())
            draw.rect(self.surface, DARK_BLUE, self.decals[1].get())

            try:
                self.drawTower(selectedTower)
            except AttributeError:
                self.drawFarm(selectedTower)

            if not self.maxLevel:
                self.upgradeButton.draw(self.surface)
            self.sellButton.draw(self.surface)

            if selectedTower.pos.getIdx(0) - rNum(300, 1).end() <= 0:
                self.x = selectedTower.pos.getIdx(0) + rNum(50, 1).end()
            else:
                self.x = selectedTower.pos.getIdx(0) - rNum(300, 1).end()

            if selectedTower.pos.getIdx(1) - rNum(300, 1).end() <= 0:
                self.y = selectedTower.pos.getIdx(1)
            else:
                self.y = selectedTower.pos.getIdx(1) - rNum(175, 1).end()
            surface.blit(self.surface, (self.x, self.y))
        except AttributeError:
            pass  # NoneType AttributeError

    def drawTower(self, selectedTower: Tower):
        throwAway = rNum(117, 1)
        self.upgradeButton.y = throwAway
        self.upgradeButton.rect.y = throwAway.get()
        throwAway.end()

        nText, dText, sText, rText = self.renderTowerText(selectedTower)

        self.updateTowerButtons(selectedTower)

        self.surface.blit(nText, self.textPos[0].get())
        self.surface.blit(dText, self.textPos[1].get())
        self.surface.blit(sText, self.textPos[2].get())
        self.surface.blit(rText, self.textPos[3].get())

        self.targetButton.draw(self.surface)

    def drawFarm(self, selectedFarm: Farm):
        throwAway = rNum(155, 1)
        self.upgradeButton.y = throwAway
        self.upgradeButton.rect.y = throwAway.get()
        throwAway.end()
        nText, mText = self.renderFarmText(selectedFarm)

        self.updateFarmButtons(selectedFarm)

        self.surface.blit(nText, self.textPos[0].get())
        self.surface.blit(mText, self.textPos[1].get())

    def updateSizes(self):
        self.surface = Surface((self.width.get(), self.height.get()))
        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))