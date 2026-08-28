from pygame import font, Surface, transform
from GameItems.autoResizableNum import rNum, rNums
from GameItems.tdColors import RED
from GameItems.game_square import GameSquare
import random

class Farm:
    class BudgetText:
        def __init__(self, amount, pos, playSpeed):
            self.amount = amount
            self.pos = pos
            self.duration = 60 / playSpeed

            self.font = font.SysFont('comicsansms', int(rNum(16, 0).end()))
            self.text = self.font.render(f'+${self.amount}', True, RED)
            self.textRect = self.text.get_rect()
            self.range = range(int(rNum(30, 0).end()), int(rNum(45, 0).end()))
            self.height = random.choice(self.range)

        def draw(self, screen):
            screen.blit(self.text, (self.pos[0] - rNum(self.textRect.width / 2, 0).end(), self.pos[1] - rNum(self.height, 0).end()))

        def countdown(self):
            self.duration -= 1
            if self.duration <= 0:
                del self

    farmList = []

    def __init__(self, farmImage, pos, upgrades, moneyGain=100, block_size=25, frames=60, price=250, playSpeed=1):
        self.image = farmImage
        self.size = rNum(block_size, 4)
        self.sizeRatio = block_size / 100
        self.pos = rNums(pos[0] * self.size.initial(), pos[1] * self.size.initial(), intList=4)
        self.moneyGain = moneyGain
        self.FPS = frames
        self.upgrades = upgrades
        self.level = 0
        self.sell_price = int(0.75 * price)
        self.selected = False
        self.center = rNums(self.pos.getIdx(0) + self.size / 2, self.pos.getIdx(1) + self.size / 2, intList=4)
        self.farmList.append(self)
        self.type = "Farm"
        self.text: None | Farm.BudgetText = None
        self.playSpeed = playSpeed

    def upgrade(self, budget):
        try:
            if budget >= self.upgrades[self.level][1]:
                self.sell_price += int(0.75 * self.upgrades[self.level][1])
                self.image = self.upgrades[self.level][2]
                self.moneyGain = self.upgrades[self.level][0]
                budget -= self.upgrades[self.level][1]
                self.level += 1
        except IndexError:
            pass
        return budget

    def sell(self, budget, blocks: list[list[GameSquare]]):
        blocks[int(self.pos.getIdx(1) / self.size)][int(self.pos.getIdx(0) / self.size)].has_tower = False
        budget += self.sell_price
        index = Farm.farmList.index(self)
        Farm.farmList.pop(index)
        del self
        return budget

    def draw(self, screen: Surface):
        try:
            screen.blit(transform.scale(self.image, (self.size.get(), self.size.get())), self.pos.get())
        except AttributeError:
            pass

    def cashOut(self):
        self.text = self.BudgetText(self.moneyGain, self.center.get(), self.playSpeed)
        return self.moneyGain