import math

from GameStates.mapSelector import MapSelector
from GameItems.tdColors import *
from GameItems.tdImages import quitImg, enemyStats, popupBackground
from pygame import draw, Surface, SRCALPHA, font
from GameItems.objects import Button, Farm, Tower, Enemy, PopupWindow, Block, SelectionBox
from GameItems.waves import difficultyEasy, waveBonusEasy
from GameItems.AutoResizableNum import *


class Game:
    blockSize = rNum(25, 1)

    def __init__(self, screen, drawingSurface: Surface, playSpeed):
        self.budget = 500
        self.health = 100

        self.screenSize = rNum(600, 1)

        self.waveNum = 20
        self.waveList = difficultyEasy
        self.waveList2 = []
        for wave in self.waveList:
            self.waveList2.append(wave)

        self.playSpeed = playSpeed

        self.unitSelected = False
        self.selectedTower: None | Tower | Farm = None
        self.placingUnit = False
        self.selectedUnit = None
        self.loadOut = None

        self.selectedMap = None
        self.chosenMap = None

        self.won = False
        self.lost = False
        self.losePopup = PopupWindow(popupBackground, text='You have lost!\nWould you like to try again?',
                                     textColor=DARK_BLUE)
        self.winPopup = PopupWindow(popupBackground, text='You have Won!\n Good Job!\nWould you like to play again?',
                                    textColor=DARK_BLUE)

        self.selectionBox = SelectionBox()

        self.font1 = font.SysFont('comicsansms', 24)
        self.font2 = font.SysFont('comicsansms', 16)
        self.font3 = font.SysFont('comicsansms', 20)

        self.paused = False

        self.animationSpeed = rNum(5, 1)
        self.hotBarRadius = rNum(40, 1)
        self.hotBarPadding = rNum(60, 1)
        self.hotBarX = rNum(50, 1)
        self.hotBarY = rNum(self.screenSize.initial() - self.hotBarRadius.initial() - self.hotBarPadding.initial(), 1)
        self.hotBarIndicator = rNums(250, 550, 100, 5, intList=1)

        self.hotBarVisible = False

        quitButton = Button(160, 400, quitImg, 0.4, 0.3)

        self.upgradeRect = None
        self.sellRect = None
        self.targetRect = None

        self.pauseMenu = Surface((500, 600), SRCALPHA)
        quitButton.draw(self.pauseMenu)

        self.screen = screen
        self.surface = drawingSurface
        size = min(screen.get_size())
        self.mainSurface = Surface((size, size), SRCALPHA)
        self.blockSurface = Surface((size, size))

    def loadLoadOut(self, loadOut):
        self.loadOut = loadOut
        # self.selectedUnit = loadOut[0]

    def update(self, name, blockSize, blockArray, clickAllowed, mousePos, clicked, surfacePos):
        mousePos = (mousePos[0] - surfacePos[0], mousePos[1] - surfacePos[1])
        self.draw(name, blockSize, blockArray, mousePos, surfacePos)
        self.selectionBox.upgradeButton.checkHovered(
            (mousePos[0] - self.selectionBox.x, mousePos[1] - self.selectionBox.y))
        self.selectionBox.targetButton.checkHovered((mousePos[0] - self.selectionBox.x, mousePos[1] - self.selectionBox.y))
        self.selectionBox.sellButton.checkHovered((mousePos[0] - self.selectionBox.x, mousePos[1] - self.selectionBox.y))
        return self.proceedWaves(clickAllowed, mousePos, clicked, name)

    def checkClicks(self, clicked, mousePos, blockArray, name, clickAllowed, offset=(0, 0)):
        mousePos = [mousePos[0] - offset[0], mousePos[1] - offset[1]]
        if clicked and not (self.won and self.lost and self.paused) and clickAllowed:
            if self.selectionBox.x <= mousePos[0] <= self.selectionBox.x + self.selectionBox.width.get() and self.selectionBox.y <= mousePos[1] <= self.selectionBox.y + self.selectionBox.height.get() and self.selectedTower:
                if self.selectedTower and self.selectedTower.level < 4:
                    if self.selectionBox.upgradeButton.checkClick():
                        self.budget = self.selectedTower.upgrade(self.budget)
                    elif self.selectionBox.targetButton.checkClick():
                        self.selectedTower.targeting += 1
                        if self.selectedTower.targeting > 4:
                            self.selectedTower.targeting = 0
                    elif self.selectionBox.sellButton.checkClick():
                        self.budget = self.selectedTower.sell(self.budget, blockArray)
                        self.unitSelected = False
                        self.selectedTower = None
            else:
                square = self.getSquare(mousePos)

                if self.placingUnit:
                    created = self.createUnit(self.selectedUnit, square, blockArray)
                    self.selectUnit(square, blockArray, Tower.tower_list)
                    if created:
                        name = "No Tower Selected"
                elif square[1] < 24 and blockArray[square[1]][square[0]].has_tower:
                    self.selectUnit(square, blockArray, Tower.tower_list)
                else:
                    if self.hotBarVisible:
                        for i in range(6):
                            iconX = self.hotBarX.get() + (self.hotBarRadius.get() + self.hotBarPadding.get()) * i
                            if math.dist((iconX, self.hotBarY.get()), mousePos) < self.hotBarRadius.get():
                                name = self.selectUnitType(i)
                    else:
                        self.selectUnit(square, blockArray, Tower.tower_list)
                        name = "No Tower Selected"
            clickAllowed = False
        return clickAllowed, name

    def proceedWaves(self, clickAllowed, mousePos, clicked, name):
        if self.health <= 0:
            return self.lose(mousePos, clicked)
        try:
            if len(Enemy.enemy_list) == 0:
                self.makeWaves(self.waveList[self.waveNum], self.chosenMap, playSpeed=self.playSpeed)
                self.waveNum += 1
                self.budget += waveBonusEasy[self.waveNum - 1]
                for farm in Farm.farmList:
                    self.budget += farm.cashOut()
        except IndexError:
            return self.win(mousePos, clicked)
        return False, True, clickAllowed, name

    def win(self, mousePos, clicked):
        menu = False
        game = True
        clickAllowed = True
        self.won = True
        if self.winPopup.optionNo.check_click(clicked, mousePos, (self.winPopup.x, self.winPopup.y)):
            game = False
            menu = True
            self.selectedMap.selected = False
            self.selectedMap = None
            clickAllowed = False
            self.playAgain()
        elif self.winPopup.optionYes.check_click(clicked, mousePos, (self.winPopup.x, self.winPopup.y)):
            self.playAgain()
            clickAllowed = False

        try:
            name = self.loadOut[0][6]
        except IndexError:
            name = self.loadOut[0][4]

        return menu, game, clickAllowed, name

    def lose(self, mousePos, clicked):
        menu = False
        game = True
        clickAllowed = True
        self.lost = True
        self.losePopup.draw(self.mainSurface)
        if self.losePopup.optionNo.check_click(clicked, mousePos, (self.losePopup.x, self.losePopup.y)):
            game = False
            menu = True
            self.selectedMap.selected = False
            self.selectedMap = None
            clickAllowed = False
            self.playAgain()
        elif self.losePopup.optionYes.check_click(clicked, mousePos, (self.losePopup.x, self.losePopup.y)):
            self.playAgain()
            clickAllowed = False

        try:
            name = self.loadOut[0][6]
        except IndexError:
            name = self.loadOut[0][4]

        return menu, game, clickAllowed, name

    def draw(self, name, blockSize, blockArray, mousePos, surfacePos):
        self.mainSurface.fill(EMPTY_COLOR)
        MapSelector.makePath(self.chosenMap, blockArray, BEIGE)

        for row in blockArray:
            for mapBlock in row:
                mapBlock.draw(self.blockSurface)

        self.enemyActions(Enemy.enemy_list)
        self.towerActions(blockSize, Tower.tower_list)

        self.renderInGameText(name, self.waveNum)

        for farm in Farm.farmList:
            if farm.text:
                farm.text.draw(self.mainSurface)
                if not self.paused:
                    farm.text.countdown()
                    if farm.text.duration <= 0:
                        farm.text = None
        if self.placingUnit:
            try:
                self.mainSurface.blit(pygame.transform.scale(self.selectedUnit[3], (blockSize.get(), blockSize.get())), (mousePos[0] - blockSize.get() / 2, mousePos[1] - blockSize.get() / 2))
                draw.circle(self.surface, OPAQUE_CYAN, (mousePos[0] + blockSize.get() / 2, mousePos[1] + blockSize.get() / 2),
                            self.selectedUnit[1] * blockSize.get())
            except TypeError:
                self.mainSurface.blit(pygame.transform.scale(self.selectedUnit[2], (blockSize.get(), blockSize.get())), (mousePos[0] - blockSize.get() / 2, mousePos[1] - blockSize.get() / 2))

        if self.paused:
            self.mainSurface.blit(self.pauseMenu, (50, 50))
        self.mainSurface.blit(self.surface, (0, 0))
        self.selectionBox.draw(self.mainSurface, self.selectedTower)
        if not self.placingUnit and not self.selectedUnit:
            self.drawTowerHotBar(mousePos)

        if self.won:
            self.winPopup.draw(self.mainSurface)

        self.screen.blit(self.blockSurface, surfacePos)
        self.screen.blit(self.mainSurface, surfacePos)

    def drawTowerHotBar(self, mousePos):
        if mousePos[1] >= self.screenSize.get() - self.hotBarRadius.get() - self.hotBarPadding.get():
            self.hotBarVisible = True
        else:
            self.hotBarVisible = False

        if self.hotBarVisible:
            if self.hotBarY.get() > self.screenSize.get() - self.hotBarRadius.get() * 1.5:
                self.hotBarY = rNum(self.hotBarY.endInitial() - self.animationSpeed.initial(), 1)
        else:
            if self.hotBarY.get() < self.screenSize.get() + self.hotBarRadius.get():
                self.hotBarY = rNum(self.hotBarY.endInitial() + self.animationSpeed.initial(), 1)
            else:
                pygame.draw.rect(self.mainSurface, DARK_BLUE, self.hotBarIndicator.get(), border_radius=3)

        for i in range(6):
            iconX = self.hotBarX.get() + (self.hotBarRadius.get() + self.hotBarPadding.get()) * i
            pygame.draw.circle(self.mainSurface, DARK_BLUE, (iconX, self.hotBarY.get()), self.hotBarRadius.get())
            pygame.draw.circle(self.mainSurface, GRAY, (iconX, self.hotBarY.get()), self.hotBarRadius.get() - 5)
            try:
                image = pygame.transform.scale(self.loadOut[i][3], (self.hotBarRadius.get(), self.hotBarRadius.get()))
            except TypeError:
                image = pygame.transform.scale(self.loadOut[i][2], (self.hotBarRadius.get(), self.hotBarRadius.get()))
            self.mainSurface.blit(image, (iconX - self.hotBarRadius.get() / 2, self.hotBarY.get() - self.hotBarRadius.get() / 2))

        for i in range(6):
            iconX = self.hotBarX.get() + (self.hotBarRadius.get() + self.hotBarPadding.get()) * i
            if math.dist((iconX, self.hotBarY.get()), mousePos) < self.hotBarRadius:
                if self.loadOut[i][-1] != 'Farm':
                    text = self.font1.render(f"${self.loadOut[i][4]}", True, LIME_GREEN2)
                else:
                    text = self.font1.render(f"${self.loadOut[i][1]}", True, LIME_GREEN2)
                textRect = text.get_rect()
                self.mainSurface.blit(text, (iconX - textRect.width / 2, self.hotBarY.get() - self.hotBarRadius.get() - textRect.height))

    def renderInGameText(self, name: str, waveNum: int):
        if self.health <= 0:
            self.health = 0

        text4 = self.font3.render(f'Money: ${self.budget}', True, RED)
        text7 = self.font3.render(f'Health: {self.health}', True, RED)
        text9 = self.font3.render(f'Selected: {name}', True, RED)
        text10 = self.font3.render(f'Wave: {waveNum} of {len(self.waveList)}', True, RED)

        self.mainSurface.blit(text4, (0, 0))
        self.mainSurface.blit(text7, (0, 30))
        self.mainSurface.blit(text9, (0, 60))
        self.mainSurface.blit(text10, (0, 90))

    def enemyActions(self, enemies: list[Enemy]):
        for enemy in enemies:
            if not self.paused:
                enemy.create_delay -= 1
            if enemy.create_delay <= 0:
                enemy.draw(self.mainSurface)
                if not self.paused:
                    self.health = enemy.move(self.health)
                    enemy.check_direction()
                    enemy.is_on_map = True
                    if enemy.fire_status or enemy.ice_status:
                        self.budget += enemy.special()
            else:
                break
            if enemy.type == 'Final Boss':
                enemy.summon()

    def towerActions(self, blockSize, towers):
        for tower in towers:
            if not self.paused:
                tower.timer -= 1
                tower.aim()
                if tower.timer <= 0:
                    self.budget += tower.get_target()
            tower.draw(self.mainSurface, OPAQUE_CYAN, self.surface)
        for tower in towers:
            for shot in tower.shotList:
                shot.draw(self.mainSurface, blockSize)
                if not self.paused:
                    shot.countDown()
        for farm in Farm.farmList:
            farm.draw(self.mainSurface)
        return int(self.budget)

    def createUnit(self, info, pos, blocks):
        """Info is list of stats for unit (damage range speed image)\n pos as block coords, not pygame coords"""
        if min(pos) > -1 and max(pos) < 25:
            if not info:
                return
            try:
                if info[4] <= self.budget and pos[1] * self.blockSize.get() < self.screenSize.get() and not blocks[pos[1]][pos[0]].is_path and not (
                        blocks[pos[1]][pos[0]].has_tower or blocks[pos[1]][pos[0]].has_farm):
                    try:
                        Tower(info[3], pos, upgrade_type=info[5], damage=info[0], attack_range=info[1], speed=info[2],
                              price=info[4], tower_type=info[6], special=info[7], playSpeed=self.playSpeed)
                        blocks[pos[1]][pos[0]].has_tower = True
                        self.budget -= info[4]
                        self.placingUnit = False
                        self.selectedUnit = None
                        return True
                    except IndexError:
                        try:
                            Tower(info[3], pos, upgrade_type=info[5], damage=info[0], attack_range=info[1], speed=info[2],
                                  price=info[4], tower_type=info[6], playSpeed=self.playSpeed)
                            blocks[pos[1]][pos[0]].has_tower = True
                            self.budget -= info[4]
                            self.placingUnit = False
                            self.selectedUnit = None
                            return True
                        except IndexError:
                            pass
            except TypeError:
                if info[1] <= self.budget and pos[1] * self.blockSize.get() < self.screenSize.get() and not blocks[pos[1]][pos[0]].is_path and not blocks[pos[1]][pos[0]].has_tower:
                    Farm(info[2], pos, info[3])
                    blocks[pos[1]][pos[0]].has_farm = True
                    self.budget -= info[1]
                    self.placingUnit = False
                    self.selectedUnit = False

    def selectUnit(self, pos, blocks, towers):
        self.selectedTower = None
        self.unitSelected = False
        try:
            if blocks[pos[1]][pos[0]].has_tower:
                for tower in towers:
                    if (round(tower.pos.getIdx(0) / self.blockSize.get()), round(tower.pos.getIdx(1) / self.blockSize.get())) == pos:
                        tower.selected = True
                        self.unitSelected = True
                        self.selectedTower = tower
                    else:
                        tower.selected = False
            elif blocks[pos[1]][pos[0]].has_farm:
                for farm in Farm.farmList:
                    if (round(farm.pos.getIdx(0) / self.blockSize.get()), round(farm.pos.getIdx(1) / self.blockSize.get())) == pos:
                        farm.selected = True
                        self.unitSelected = True
                        self.selectedTower = farm
                    else:
                        farm.selected = False
            else:
                for unselectingTowers in towers:
                    unselectingTowers.selected = False
        except IndexError:
            pass

    def selectUnitType(self, loadOutNumber, n=None):
        def selectInfo(num: int):
            unitType = self.loadOut[num]
            try:
                name = self.loadOut[num][6]
            except IndexError:
                name = self.loadOut[num][4]
            return unitType, name

        self.selectedTower = None
        for tower in Tower.tower_list:
            tower.selected = False

        if n is not None:
            self.selectedUnit, unitName = selectInfo(n)
            self.placingUnit = True
            return unitName

        self.selectedUnit, unitName = selectInfo(loadOutNumber)
        self.placingUnit = True
        return unitName

    def playAgain(self):
        self.waveList = []
        for wave in self.waveList2:
            self.waveList.append(wave)
        for tower in Tower.tower_list:
            tower.selected = False
        for farm in Farm.farmList:
            farm.selected = False
        Tower.tower_list = []
        Enemy.enemy_list = []
        Farm.farmList = []
        for block in Block.block_list:
            block.has_tower = False
            block.changeColor(reset=True)
        self.unitSelected = False
        self.selectedUnit = self.loadOut[0]
        self.surface.fill(EMPTY_COLOR)
        self.health = 100
        self.budget = 500
        self.waveNum = 0
        self.won = False
        self.lost = False

    def updateSize(self):
        size = min(self.surface.get_size())
        self.mainSurface = Surface((size, size), SRCALPHA)
        self.blockSurface = Surface((size, size))

    @staticmethod
    def makeWaves(waveList: list, path: list, playSpeed: float):
        for wave in waveList:
            index = waveList.index(wave)
            for i in range(wave[1]):
                if index == 0 and i == 0:
                    delay = 3 / playSpeed
                else:
                    delay = wave[2] / playSpeed
                waveStats = enemyStats[wave[0]]
                Enemy(waveStats[0], [path[0][0] * Game.blockSize.initial(), path[0][1] * Game.blockSize.initial()], path, waveStats[1], waveStats[2],
                      waveStats[3], delay=delay, playSpeed=playSpeed, unitType=wave[0])

    @staticmethod
    def getSquare(pos):
        clicked_on_block = (int(pos[0] / Game.blockSize.get()), int(pos[1] / Game.blockSize.get()))
        return clicked_on_block
