import math
from random import choice

import pygame.transform
from pygame import font, transform, draw, mouse, Surface, Color, mixer
from GameItems.tdColors import *
from GameItems.tdImages import enemyStats, iceImg, fireImg, checkImg, xImg
from GameItems.AutoResizableNum import *

mixer.init()
font.init()

"""Object definition for my Tower Defense Game"""


def pygameCoordsToImageCoords(coords, origin):
    x = coords[0]
    y = coords[1]
    ox = origin[0]
    oy = origin[1]
    newX = x - ox
    newY = oy - y
    return [newX, newY]


def createAngleFromOrigin(pos, origin):
    X, Y = pygameCoordsToImageCoords(pos, origin)
    angleFromOrigin = 0

    try:
        angleFromOrigin = math.degrees(math.atan(Y / X))
    except ZeroDivisionError:
        if Y > 0:
            return 90
        elif Y < 0:
            return 270

    if not angleFromOrigin and X < 0:
        return 180

    if X < 0 < Y:
        angleFromOrigin += 180
    if X < 0 > Y:
        angleFromOrigin += 180
    return angleFromOrigin


def imageScaleByRatio(img: Surface, scaleRatio):
    width = img.get_width() * scaleRatio
    height = img.get_height() * scaleRatio
    scaledImg = transform.scale(img, (width, height))
    return scaledImg


def blitText(surface: Surface, text: str, yPos, writtenFont: font.Font,
             color: Color | tuple[int, int, int] = Color('black')):
    words = [word.split(' ') for word in text.splitlines()]
    max_width = surface.get_width() * (11 / 12)
    word_surface = None
    for line in words:
        writtenLine = ''
        for word in line:
            if writtenLine:
                writtenLine += f' {word}'
            else:
                writtenLine += word
            if writtenFont.render(writtenLine, False, color).get_width() < max_width:
                word_surface = writtenFont.render(writtenLine, False, color)
            else:
                wordWidth, wordHeight = word_surface.get_size()
                surface.blit(word_surface, ((surface.get_width() - wordWidth) / 2, yPos))
                yPos += wordHeight
                writtenLine = word
                if writtenLine == line[-1]:
                    word_surface = writtenFont.render(writtenLine, False, color)
        wordWidth, wordHeight = word_surface.get_size()
        surface.blit(word_surface, ((surface.get_width() - wordWidth) / 2, yPos))
        yPos += wordHeight


def customRound(num: float, roundedTo: float):
    counter = 0
    while roundedTo < 1:
        num *= 10
        roundedTo *= 10
        counter += 1
    num = round(num)
    num /= 10 ** counter
    return num


def rotationMatrix(point, angle):
    newX = point[0] * math.cos(math.radians(angle)) - point[1] * math.sin(math.radians(angle))
    newY = point[0] * math.sin(math.radians(angle)) + point[1] * math.cos(math.radians(angle))
    return newX, newY


class Block:            # Autoresize check
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
            Block.menu_block_list.append(self)
        else:
            Block.block_list.append(self)

    def changeColor(self, color=BEIGE, reset=False):
        if reset:
            self.color = self.initialColor
        else:
            self.color = color

    def draw(self, screen):
        draw.rect(screen, self.color, [self.location[0].get(), self.location[1].get(), int(self.size.get()+1), int(self.size.get()+1)], 0)


class Enemy:
    enemy_list = []

    def __init__(self, img, start, path, health, speed=1, size=64, delay: float = 1, frames=60, playSpeed=1, unitType=None):
        size = rNum(size, 3)
        if speed > size.initial():
            speed = size.initial()
        self.image = img
        self.location = list(map(lambda a: rNum(a, 3), start))
        self.size = size
        self.path = path
        self.health = health
        self.initial_health = health
        self.target_number = 1
        self.last_targeted_location = self.path[0]
        self.target_location = self.path[self.target_number]
        self.targeted_coord = [rNum(self.target_location[0] * self.size.initial(), 3), rNum(self.target_location[1] * self.size.initial(), 3)]
        self.speed = speed * playSpeed
        self.original_speed = speed * playSpeed
        self.playSpeed = playSpeed
        self.frames = frames
        self.create_delay = delay * frames
        self.direction = 0
        self.type = unitType
        self.is_on_map = False
        self.fire_status = []  # intensity/timer
        self.ice_status = []
        self.fire = fireImg
        self.ice = iceImg
        self.summonDelay = 10 * frames / self.playSpeed
        self.deathAudio: mixer.Sound | None = None  # bongSong
        Enemy.enemy_list.append(self)

    def check_death(self):
        if self.health <= 0:
            try:
                index = Enemy.enemy_list.index(self)
                Enemy.enemy_list.pop(index)
                if self.deathAudio:
                    self.deathAudio.play()
            except ValueError:
                pass
            self.size.end()
            self.location[0].end()
            self.location[1].end()
            del self

    def draw(self, screen: Surface):
        img = pygame.transform.scale(self.image, (self.size.get(), self.size.get()))
        screen.blit(img, (self.location[0].get(), self.location[1].get()))
        draw.rect(screen, (255, 0, 0), [self.location[0].get(), self.location[1].get(), self.size.get() * self.health / self.initial_health, 2])
        if self.fire_status:
            screen.blit(pygame.transform.scale(self.fire, (self.size.get(), self.size.get())), (self.location[0].get(), self.location[1].get()))
        if self.ice_status:
            screen.blit(pygame.transform.scale(self.ice, (self.size.get(), self.size.get())), (self.location[0].get(), self.location[1].get()))

    def check_direction(self):
        def rotateImages(angle):
            self.image = transform.rotate(self.image, angle)
            self.fire = transform.rotate(self.fire, angle)
            self.ice = transform.rotate(self.ice, angle)

        last_x = self.last_targeted_location[0]
        last_y = self.last_targeted_location[1]
        current_x = self.target_location[0]
        current_y = self.target_location[1]
        if last_x == current_x:
            if last_y < current_y and self.direction != 0:
                if self.direction == 90:
                    rotateImages(-90)
                    self.direction = 0
                elif self.direction == 270:
                    rotateImages(90)
                    self.direction = 0
            elif current_y < last_y and self.direction != 180:
                if self.direction == 270:
                    rotateImages(-90)
                    self.direction = 180
                elif self.direction == 90:
                    rotateImages(90)
                    self.direction = 180
        else:
            if last_x < current_x and self.direction != 90:
                if self.direction == 0:
                    rotateImages(90)
                    self.direction = 90
                elif self.direction == 180:
                    rotateImages(-90)
                    self.direction = 90
            elif current_x < last_x and self.direction != 270:
                if self.direction == 180:
                    rotateImages(90)
                    self.direction = 270
                elif self.direction == 0:
                    rotateImages(-90)
                    self.direction = 270

    def special(self):
        added_budget = 0
        if self.fire_status:
            self.fire_status[1] -= 1 * self.playSpeed
            if not self.fire_status[1] % self.frames:
                if self.health <= self.fire_status[0] * self.playSpeed:
                    added_budget = self.health
                    self.health = 0
                    self.check_death()
                else:
                    self.health -= self.fire_status[0] * self.playSpeed
                    added_budget = self.fire_status[0] * self.playSpeed
            if self.fire_status[1] <= 0:
                self.fire_status = []
        if self.ice_status:
            self.ice_status[1] -= 1 * self.playSpeed
            if self.ice_status[1]:
                self.speed = self.original_speed * (1 - self.ice_status[0])
            else:
                self.speed = self.original_speed
                self.ice_status = []
        return added_budget

    def move(self, health):
        try:
            distance = math.dist((self.location[0].end(), self.location[1].end()), (self.targeted_coord[0].end(), self.targeted_coord[1].end()))
            if distance < self.speed:
                self.location = [rNum(self.targeted_coord[0].initial(), 3), rNum(self.targeted_coord[1].initial(), 3)]
                self.target_number += 1

            self.last_targeted_location = self.path[self.target_number - 1]
            self.target_location = self.path[self.target_number]

            self.targeted_coord = [rNum(self.target_location[0] * self.size.initial(), 3), rNum(self.target_location[1] * self.size.initial(), 3)]

            if self.location[0].get() > self.targeted_coord[0].get():
                self.location[0] = rNum(self.location[0].initial() - self.speed, 3)
            elif self.location[0].get() < self.targeted_coord[0].get():
                self.location[0] = rNum(self.location[0].initial() + self.speed, 3)
            elif self.location[1].get() > self.targeted_coord[1].get():
                self.location[1] = rNum(self.location[1].initial() - self.speed, 3)
            elif self.location[1].get() < self.targeted_coord[1].get():
                self.location[1] = rNum(self.location[1].initial() + self.speed, 3)
        except IndexError:
            index = Enemy.enemy_list.index(self)
            Enemy.enemy_list.pop(index)
            health -= self.health
            del self
        return health

    def summon(self):
        self.summonDelay -= 1
        summonedNumber = 0
        if self.summonDelay == 0:
            summonNumber = 10
            enemyTypes = ["Normal", "Slow", "Fast", "Tank", "Boss", "Slow Boss", 'Fast Boss', "Tank Boss"]
            enemySummonValues = {"Normal": 1, "Slow": 1, "Fast": 1, "Tank": 2, "Boss": 2, "Slow Boss": 3,
                                 'Fast Boss': 4, "Tank Boss": 8}
            while summonNumber > 0:
                newEnemy = choice(enemyTypes)
                if summonNumber >= enemySummonValues[newEnemy]:
                    summonedNumber += 1
                    summonNumber -= enemySummonValues[newEnemy]
                    stats = enemyStats[newEnemy]
                    newEnemy = Enemy(stats[0], (self.location[0].initial(), self.location[1].initial()), self.path, stats[1], stats[2], size=stats[3],
                                     delay=0.1 * summonNumber, playSpeed=self.playSpeed, unitType=newEnemy)
                    newEnemy.target_number = self.target_number
                    newEnemy.direction = self.direction
            self.summonDelay = 10 * self.frames / self.playSpeed

    def __str__(self) -> str:
        return str(self.type)


class Farm:
    class BudgetText:
        def __init__(self, amount, pos, playSpeed):
            self.amount = amount
            self.pos = pos
            self.duration = 60 / playSpeed

            self.font = font.SysFont('comicsansms', 16)
            self.text = self.font.render(f'+${self.amount}', True, RED)
            self.textRect = self.text.get_rect()
            self.range = range(30, 45)
            self.height = choice(self.range)

        def draw(self, screen):
            screen.blit(self.text, (self.pos[0] - self.textRect.width / 2, self.pos[1] - self.height))

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
        self.center = [self.pos.getIdx(0) + self.size.get() / 2, self.pos.getIdx(1) + self.size.get() / 2]
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

    def sell(self, budget, blocks: list[list[Block]]):
        blocks[int(self.pos.getIdx(1) / self.size.get())][int(self.pos.getIdx(0) / self.size.get())].has_tower = False
        budget += self.sell_price
        index = Farm.farmList.index(self)
        Farm.farmList.pop(index)
        del self
        return budget

    def draw(self, screen: Surface):
        try:
            screen.blit(self.image, self.pos.get())
        except AttributeError:
            pass

    def cashOut(self):
        self.text = self.BudgetText(self.moneyGain, self.center, self.playSpeed)
        return self.moneyGain


class Tower:
    tower_list = []
    scout_count = 0
    sniper_count = 0
    minigunner_count = 0
    turret_count = 0
    pyro_count = 0
    freezer_count = 0
    demo_count = 0
    rifle_count = 0
    targetOptions = ['First', 'Close', 'Strong', 'Weak', 'Last']

    class Shot:
        def __init__(self, start, end, originList, color=(255, 255, 255), playSpeed=1):
            self.start = start
            self.end = end
            self.shootingTimer = 3 / playSpeed
            self.originList = originList
            self.color = color
            self.playSpeed = playSpeed
            self.explosion = False
            self.expRange = 0
            self.explosionTimer = 0

        def explode(self, explosionRange):
            self.explosionTimer = 12 / self.playSpeed
            self.explosion = True
            self.expRange = explosionRange

        def draw(self, screen: Surface, blockSize):
            if self.shootingTimer > 0:
                draw.line(screen, color=self.color, start_pos=(self.start[0].get(), self.start[1].get()), end_pos=(self.end[0], self.end[1]))
            if self.explosion:
                draw.circle(screen, color=self.color, center=(self.end[0], self.end[1]), radius=self.expRange * blockSize.get())

        def countDown(self):
            self.shootingTimer -= 1
            self.explosionTimer -= 1
            if self.shootingTimer <= 0 and self.explosionTimer <= 0:
                self.start[0].end()
                self.start[1].end()
                self.originList.remove(self)

    def __init__(self, towerImage: Surface, pos, upgrade_type, block_size=25, attack_range=3, damage=1, speed=1, frames=60, price=100, special=None, tower_type=None, playSpeed=1):
        """Range in pixels, speed in seconds"""
        block_size = rNum(block_size, 4)
        self.target = None
        self.selectedShotStart = None
        self.shotStartingCoord = None
        self.drawnImg = None
        self.image = transform.scale(towerImage, (rNum(100, 4).endInitial(), rNum(100, 4).endInitial()))
        self.block_size = block_size
        self.sizeRatio = rNum(block_size.initial() / 100, 4)
        self.pos = rNums(pos[0] * block_size.initial(), pos[1] * block_size.initial(), intList=4)
        self.range = attack_range
        self.damage = damage
        self.speed = speed / playSpeed
        self.shotList = []
        self.playSpeed = playSpeed
        self.frames = frames
        self.timer = 0
        self.selected = False
        self.level = 0
        self.angleToTarget = 0
        self.upgrades = upgrade_type
        self.sell_price = int(0.75 * price)
        self.special = special
        self.targeting = 0  # 0 = First, 1 = Close, 2 = Strong, 3 = Weak, 4 = Last
        self.type = tower_type
        self.center = rNums(self.pos.initialIdx(0) + self.block_size.initial() / 2, self.pos.initialIdx(1) + self.block_size.initial() / 2, intList=4)
        Tower.tower_list.append(self)
        if tower_type == 'Scout':
            Tower.scout_count += 1
            self.shotStart = [[[4, 23]], [[4, 23]], [[4, 23]], [[4, 23], [21, 23]], [[4, 23], [21, 23]]]
        elif tower_type == 'Sniper':
            Tower.sniper_count += 1
            self.shotStart = [[[17, 24]], [[17, 24]], [[17, 24]], [[17, 24]], [[17, 24]]]
        elif tower_type == 'Rifle':
            Tower.rifle_count += 1
            self.shotStart = [[[17, 20]], [[17, 20]], [[17, 20]], [[17, 20]], [[17, 20]]]
        elif tower_type == 'Minigunner':
            Tower.minigunner_count += 1
            self.shotStart = [[[21, 25]], [[21, 25]], [[21, 25]], [[21, 25], [4, 25]], [[21, 25], [4, 25]]]
        elif tower_type == 'Turret':
            Tower.turret_count += 1
            self.shotStart = [[[12, 19]], [[12, 19]], [[12, 19], [3, 19]], [[12, 19], [3, 19]],
                              [[21, 19], [3, 19], [12, 22]]]
        elif tower_type == 'Pyromaniac':
            Tower.pyro_count += 1
            self.special_type = 'Fire'
            self.shotStart = [[[21, 21]], [[21, 21]], [[21, 21]], [[21, 21]], [[21, 21]]]
        elif tower_type == 'Freezer':
            Tower.freezer_count += 1
            self.special_type = 'Ice'
            self.shotStart = [[[4, 24]], [[4, 24]], [[4, 24]], [[4, 24]], [[4, 24], [21, 24]]]
        elif tower_type == 'Demolition':
            Tower.demo_count += 1
            self.special_type = 'Demo'
            self.shotStart = [[[4, 25]], [[4, 25]], [[4, 25]], [[4, 25], [21, 25]], [[21, 25], [4, 25]]]

    def attack(self, target: Enemy):
        try:
            added_budget = 0
            if target.health < self.damage:
                added_budget += target.health
            else:
                added_budget += self.damage
            target.health -= self.damage
        except AttributeError:
            return 0
        self.timer = self.speed * self.frames  # time in frames per second

        self.calculateShotStartPos()
        newShot = self.Shot(self.shotStartingCoord,
                            [target.location[0].get() + target.size.get() / 2, target.location[1].get() + target.size.get() / 2], self.shotList,
                            playSpeed=self.playSpeed)
        if self.type == 'Pyromaniac':
            newShot.color = ORANGE
        elif self.type == 'Freezer':
            newShot.color = CYAN
        elif self.type == 'Demolition':
            newShot.color = ORANGE
            newShot.explode(self.special[0])
        self.shotList.append(newShot)

        target.check_death()
        if self.special:
            added_budget += self.special_attack(target)
        return added_budget

    def calculateShotStartPos(self):
        if len(self.shotStart[self.level]) > 1:
            try:
                if self.shotStart[self.level].index(self.selectedShotStart) == len(self.shotStart[self.level]) - 1:
                    self.selectedShotStart = self.shotStart[self.level][0]
                else:
                    self.selectedShotStart = self.shotStart[self.level][
                        self.shotStart[self.level].index(self.selectedShotStart) + 1]
            except AttributeError:
                self.selectedShotStart = self.shotStart[self.level][0]
            except ValueError:
                self.selectedShotStart = self.shotStart[self.level][0]
        else:
            self.selectedShotStart = self.shotStart[self.level][0]
        imageCoord = pygameCoordsToImageCoords(self.selectedShotStart, [self.block_size.initial() / 2, self.block_size.initial() / 2])
        newShotStart = rotationMatrix(imageCoord, self.angleToTarget)
        self.shotStartingCoord = [rNum(self.center.initialIdx(0) + newShotStart[0], 4), rNum(self.center.initialIdx(1) - newShotStart[1], 4)]

    def special_attack(self, target: Enemy):
        addedBudget = 0
        try:
            if self.special_type == 'Fire':
                target.fire_status = [self.special[0], self.special[1]]
            elif self.special_type == 'Ice':
                target.ice_status = [self.special[0], self.special[1]]
            elif self.special_type == 'Demo':
                addedBudget = self.explosionAttack(target)
        except AttributeError:
            pass
        return addedBudget

    def explosionAttack(self, target):
        enemiesWithinDistance: list[Enemy] = []
        for enemy in Enemy.enemy_list:
            if enemy != target:
                if math.dist((enemy.location[0].get(), enemy.location[1].get()), (target.location[0].get(), target.location[1].get())) <= self.special[0] * self.block_size.get() and enemy.is_on_map:
                    enemiesWithinDistance.append(enemy)
        addedBudget = 0
        for enemy in enemiesWithinDistance:
            if 0 < enemy.health < self.special[1]:
                addedBudget += enemy.health
            else:
                addedBudget += self.special[1]
            enemy.health -= self.special[1]
            enemy.check_death()
        return addedBudget

    def upgrade(self, budget):
        try:
            if budget >= self.upgrades[self.level][3]:
                self.sell_price += int(0.75 * self.upgrades[self.level][3])
                self.image = transform.scale(self.upgrades[self.level][4], (rNum(100, 4).endInitial(), rNum(100, 4).endInitial()))
                self.aim()
                budget -= self.upgrades[self.level][3]
                self.range += self.upgrades[self.level][0]
                self.damage += self.upgrades[self.level][1]
                self.speed -= self.upgrades[self.level][2] / self.playSpeed
                try:
                    self.special = self.upgrades[self.level][5]  # always run last
                except IndexError:
                    pass
                self.level += 1
        except IndexError:
            pass
        return budget

    def sell(self, budget, blocks: list[list[Block]]):
        self.sizeRatio.end()
        self.center.end()
        blocks[int(self.pos.endIdx(1) / self.block_size.get())][int(self.pos.endIdx(0) / self.block_size.end())].has_tower = False
        budget += self.sell_price
        index = Tower.tower_list.index(self)
        Tower.tower_list.pop(index)
        del self
        return budget

    def draw(self, screen: Surface, color, surface):
        try:
            if self.selected:
                draw.circle(surface, color, (self.pos.getIdx(0) + self.block_size.get() / 2, self.pos.getIdx(1) + self.block_size.get() / 2),
                            self.range * self.block_size.get())
            screen.blit(self.drawnImg, [self.center.getIdx(0) - self.drawnImg.get_width() / 2,
                                        self.center.getIdx(1) - self.drawnImg.get_height() / 2])
        except AttributeError:
            self.aim()

    def get_target(self):
        added_budget = 0
        enemy_distance_list: dict[float, Enemy] = {}
        if self.type == 'Pyromaniac':
            for enemy in Enemy.enemy_list:
                distance = math.dist((enemy.location[0].get(), enemy.location[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1)))
                if distance < self.range * self.block_size.get() and not enemy.fire_status:
                    enemy_distance_list[distance] = enemy
                pass
        elif self.type == 'Freezer':
            for enemy in Enemy.enemy_list:
                distance = math.dist((enemy.location[0].get(), enemy.location[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1)))
                if distance < self.range * self.block_size.get() and not enemy.ice_status:
                    enemy_distance_list[distance] = enemy
        else:
            for enemy in Enemy.enemy_list:
                distance = math.dist((enemy.location[0].get(), enemy.location[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1)))
                if distance < self.range * self.block_size.get():
                    enemy_distance_list[distance] = enemy
        if self.targeting == 0:  # targeting first
            first = None
            for enemy in enemy_distance_list:
                if not first:
                    first = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].target_number > first.target_number:
                        first = enemy_distance_list[enemy]
            self.target = first
        elif self.targeting == 1:  # targeting closest
            try:
                self.target = enemy_distance_list[min(enemy_distance_list)]
            except ValueError:
                pass
        elif self.targeting == 2:  # targeting strongest
            strong = None
            for enemy in enemy_distance_list:
                if not strong:
                    strong = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].health > strong.health:
                        strong = enemy_distance_list[enemy]
            self.target = strong
        elif self.targeting == 3:  # targeting weakest
            weak = None
            for enemy in enemy_distance_list:
                if not weak:
                    weak = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].health < weak.health:
                        weak = enemy_distance_list[enemy]
            self.target = weak
        elif self.targeting == 4:  # targeting last
            last = None
            for enemy in enemy_distance_list:
                if not last:
                    last = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].target_number < last.target_number:
                        last = enemy_distance_list[enemy]
            self.target = last
        if self.target:
            if self.target.is_on_map:
                added_budget = self.attack(self.target)
        return added_budget

    def aim(self):
        try:
            target_pos = self.target.location
        except AttributeError:
            self.drawnImg = transform.rotate(self.image, self.angleToTarget)
            try:
                self.drawnImg = imageScaleByRatio(self.drawnImg, self.sizeRatio.get())
                return
            except AttributeError:
                self.drawnImg = imageScaleByRatio(self.image, self.sizeRatio.get())
                return
        try:
            self.angleToTarget = createAngleFromOrigin((target_pos[0].get(), target_pos[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1))) + 90
            self.drawnImg = transform.scale(self.image, (self.block_size.get(), self.block_size.get()))
            self.drawnImg = transform.rotate(self.drawnImg, self.angleToTarget)
        except AttributeError:
            pass

    def __str__(self) -> str:
        return str(self.type)


class Button:               # Autoresize check
    buttons = []

    def __init__(self, x, y, buttonImage: Surface, x_scale, y_scale):
        self.ogImg = buttonImage
        self.x = rNum(x, 1)
        self.y = rNum(y, 1)
        self.width = rNum(self.ogImg.get_width() * x_scale, 1)
        self.height = rNum(self.ogImg.get_height() * y_scale, 1)
        self.image = transform.scale(self.ogImg, (self.width.get(), self.height.get()))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x.get(), self.y.get())
        self.clicked = False

        self.command = None
        self.args = None

        self.buttons.append(self)

    def draw(self, surface: Surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def check_click(self, clicked, mousePos, offset=(0, 0)):
        action = False
        pos = (mousePos[0] - offset[0], mousePos[1] - offset[1])

        if self.rect.collidepoint(pos) and clicked and not self.clicked:
            self.clicked = True
            action = True
        if not clicked:
            self.clicked = False
        return action

    def checkClick(self, offset=(0, 0)):
        pos = (mouse.get_pos()[0] - offset[0], mouse.get_pos()[1] - offset[1])

        if self.rect.collidepoint(pos):
            if mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                self.command(*self.args)
        if not mouse.get_pressed()[0]:
            self.clicked = False

    def updateSizes(self):
        self.image = transform.scale(self.ogImg, (self.width.get(), self.height.get()))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x.get(), self.y.get())


class NoImgButton:      # Autoresize check
    buttons = []

    def __init__(self, x, y, w, h, bgColor, fgColor, hovColor, text, fontSize=24, command=None, textColor=None):
        self.x, self.y, self.w, self.h = rNum(x, 1), rNum(y, 1), rNum(w, 1), rNum(h, 1)
        self.fontSize = rNum(fontSize, 1)
        self.rect = pygame.Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
        self.command = command
        self.bgColor = bgColor
        self.textColor = textColor
        self.fgColor = fgColor
        self.hoveredColor = hovColor
        self.hovering = False

        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))
        self.buttonText = text
        self.text = self.font.render(self.buttonText, False, self.textColor if self.textColor else self.bgColor, None)
        self.tRect = self.text.get_rect()
        self.tRect.center = self.rect.center

        self.buttons.append(self)

    def checkHovered(self, mousePos, offset=(0, 0)):
        self.hovering = self.rect.collidepoint((mousePos[0] - offset[0], mousePos[1] - offset[1]))
        return self.hovering

    def checkClick(self):
        if self.hovering:
            if self.command:
                self.command()
            return True
        return False

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.bgColor, self.rect)
        if self.hovering:
            pygame.draw.rect(surface, self.hoveredColor,
                             (self.rect.x + 5, self.rect.y + 5, self.rect.w - 10, self.rect.h - 10))
        else:
            pygame.draw.rect(surface, self.fgColor,
                             (self.rect.x + 5, self.rect.y + 5, self.rect.w - 10, self.rect.h - 10))

        surface.blit(self.text, self.tRect)

    def update(self, text: str):
        self.text = self.font.render(text, False, self.textColor if self.textColor else self.bgColor, None)
        self.tRect = self.text.get_rect()
        self.tRect.center = self.rect.center

    def updateSizes(self):
        self.rect.update(int(self.x.get()), int(self.y.get()), int(self.w.get()), int(self.h.get()))
        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))
        self.text = self.font.render(self.buttonText, False, self.textColor if self.textColor else self.bgColor, None)
        self.tRect = self.text.get_rect()
        self.tRect.center = self.rect.center


class Map:          # Autoresize check
    def __init__(self, mapList, location, value):
        self.map = mapList
        self.location = tuple(map(lambda a: rNum(a, 1), location))
        self.array: list[list[Block]] = []
        self.value = value
        self.selected = False
        self.miniBlockSize = rNum(5, 1)

    def create_array(self):
        if self.array:
            self.array = []
        for i in range(24):
            self.array.append([])
            for j in range(24):
                block = Block((self.location[0].initial() + j * self.miniBlockSize.initial(), self.location[1].initial() + i * self.miniBlockSize.initial()), (0, 128, 0), 5, True)
                self.array[i].append(block)


class MapsPage:         # Autoresize check
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


class Slider:           # Autoresize check
    sliders = []

    def __init__(self, **kwargs):
        options = {
            "x": 0,
            "y": 0,
            "min": 0,
            "max": 1,
            "height": 25,
            "width": 100,
            "bg": (128, 128, 128),
            "fg": (255, 255, 255),
            "fillColor": (255, 0, 0),
            "nobScale": .35,
            "interval": 1,
            "value": 0
        }
        options.update(kwargs)
        self.x = 0
        self.y = 0
        self.min = 0
        self.max = 1
        self.height = 25
        self.width = 100

        self.bgColor = (128, 128, 128)
        self.fgColor = (255, 255, 255)
        self.fillColor = (255, 0, 0)

        self.value = 0
        self.nobScale = 0.35
        self.held = False

        self.interval = 1

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.x = rNum(self.x, 1)
        self.y = rNum(self.y, 1)
        self.height = rNum(self.height, 1)
        self.width = rNum(self.width, 1)

        self.fontSize = rNum(24, 1)

        self.borderWidth = rNum(int(self.height.initial() * (1 / 3)), 1)
        self.slideXMax = rNum(self.x.initial() + self.width.initial() - self.borderWidth.initial(), 1)
        self.slideXMin = rNum(self.x.initial() + self.borderWidth.initial(), 1)
        self.slideDifference = rNum(self.slideXMax.initial() - self.slideXMin.initial(), 1)

        if self.value <= self.min:
            self.value = self.min
            self.slideX = self.slideXMin.get()
        else:
            self.slideX = self.slideDifference.get() * (self.value / self.max) + self.slideXMin.get()

        Slider.sliders.append(self)

    def checkClickPos(self, offset=(0, 0)):
        mousePos = mouse.get_pos()
        mousePos = (mousePos[0] - offset[0], mousePos[1] - offset[1])
        dist = math.dist(mousePos, (self.slideX, self.y.get() + self.height.get() / 2))
        if dist <= self.height.get() * self.nobScale:
            return True
        return False

    def getValue(self):
        lowValue = self.slideX - self.slideXMin.get()
        percent = lowValue / self.slideDifference.get()
        self.value = customRound(((self.max - self.min) * percent) + self.min, self.interval)
        return self.value

    def slide(self, surfacePos):
        clicked = False
        if self.held:
            clicked = True
        elif mouse.get_pressed()[0]:
            clicked = self.checkClickPos(surfacePos)
        if not mouse.get_pressed()[0]:
            self.held = False
            clicked = False
        if clicked:
            self.held = True
            self.slideX = mouse.get_pos()[0] - surfacePos[0]
        if self.slideX >= self.slideXMax.get():
            self.slideX = self.slideXMax.get()
        elif self.slideX <= self.slideXMin.get():
            self.slideX = self.slideXMin.get()
        self.getValue()

    def draw(self, screen: Surface):
        draw.rect(screen, self.bgColor, (self.x.get(), self.y.get(), self.width.get(), self.height.get()))
        draw.rect(screen, (0, 0, 0), (self.x.get() + self.borderWidth.get(), self.y.get() + self.borderWidth.get(), self.width.get() - 2 * self.borderWidth.get(), self.height.get() - 2 * self.borderWidth.get()))
        draw.rect(screen, self.fillColor, (self.x.get() + self.borderWidth.get(), self.y.get() + self.borderWidth.get(), self.slideX - self.x.get() - 2, self.height.get() - 2 * self.borderWidth.get()))
        draw.circle(screen, self.fgColor, (self.slideX, self.y.get() + self.height.get() / 2), self.height.get() * self.nobScale)

        f = font.SysFont('comicsansms', int(self.fontSize.get()))
        t = f.render(f"{self.value}", False, BLUE, None)
        screen.blit(t, (self.x.get(), self.y.get()))


class PopupWindow:          # Autoresize check
    windows = []

    def __init__(self, img: Surface, **kwargs) -> None:
        self.img = img
        self.fontSize = rNum(24, 1)
        options = {
            "centering": True,
            'x': None,
            'y': None,
            "scale": [1, 1],
            "text": "This should be a message to the user, but no matter the message it will be centered, but if it gets too long it will go underneath the buttons",
            "textColor": (0, 0, 0),
            "optionNum": 2
        }
        options.update(kwargs)
        self.centering = options["centering"]
        if not self.centering:
            self.x = rNum(options['x'], 1)
            self.y = rNum(options['y'], 1)
        else:
            self.x = 0
            self.y = 0

        self.numOfOptions = options["optionNum"]

        self.imageSize = (rNum(self.img.get_width() * options["scale"][0], 1), rNum(self.img.get_height() * options["scale"][1], 1))
        self.buttonSize = (75 * options["scale"][0], 75 * options["scale"][1])

        self.image = transform.scale(self.img, (self.imageSize[0].get(), self.imageSize[1].get()))
        if self.numOfOptions == 2:
            self.optionYes = Button(self.image.get_width() * (1 / 6), self.image.get_height() * (2 / 3), transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
            self.optionNo = Button(self.image.get_width() * (7 / 12), self.image.get_height() * (2 / 3), transform.scale(xImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
        elif self.numOfOptions == 1:
            self.optionYes = Button(self.image.get_width() * (3 / 8), self.image.get_height() * (2 / 3), transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
            self.optionNo = None

        self.textColor = options["textColor"]
        self.text = options["text"]

        self.surface = Surface((int(self.imageSize[0].get()), int(self.imageSize[1].get())))

        self.windows.append(self)

    def draw(self, surface: Surface):
        f = pygame.font.SysFont('comicsansms', int(self.fontSize.get()))
        self.surface.blit(self.image, (0, 0))
        blitText(self.surface, self.text, (self.image.get_height() * (1 / 12)), f, color=self.textColor)
        self.optionYes.draw(self.surface)
        if self.optionNo:
            self.optionNo.draw(self.surface)
        if self.centering:
            self.x = (surface.get_width() - self.image.get_width()) / 2
            self.y = (surface.get_height() - self.image.get_height()) / 2
            surface.blit(self.surface, (self.x, self.y))
        else:
            surface.blit(self.surface, (self.x.get(), self.y.get()))

    def updateSizes(self):
        self.image = transform.scale(self.img, (self.imageSize[0].get(), self.imageSize[1].get()))
        self.surface = Surface((int(self.imageSize[0].get()), int(self.imageSize[1].get())))


class OptionBox:            # Autoresize check
    boxes = []

    def __init__(self, x, y, w, h, color, highlight_color, option_list, selected=0, rightEdge=rNum(600, 1),
                 scrollPosition=0):
        self.x = rNum(x, 1)
        self.y = rNum(y, 1)
        self.w = rNum(w, 1)
        self.h = rNum(h, 1)
        self.fontSize = rNum(24, 1)

        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
        self.font = pygame.font.SysFont('comicsansms', int(self.fontSize.get()))
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.maxOptions = 6  # MUST BE EVEN NUMBER
        self.scrollPosition = scrollPosition
        self.rightMost = rightEdge
        if self.rect.x - self.rect.width / 2 <= 0:
            self.leftEdge = True
        else:
            self.leftEdge = False
        if self.rect.x + self.rect.width * (3 / 2) >= self.rightMost.get():
            self.rightEdge = True
        else:
            self.rightEdge = False

        self.boxes.append(self)

    def draw_scroll_bar(self, screen, x):
        scroll_bar_height = int(self.maxOptions / 2) * self.rect.height / (len(self.option_list) - self.maxOptions + 1)
        scroll_bar_y = self.rect.y + self.rect.height + scroll_bar_height * self.scrollPosition  # / self.maxOptions
        scroll_bar_rect = pygame.Rect(x, scroll_bar_y, 10, scroll_bar_height)
        pygame.draw.rect(screen, DARK_BLUE, scroll_bar_rect)

    def getRectPos(self, rect, iterable):
        if iterable >= self.maxOptions // 2:
            if self.rightEdge:
                rect.x = self.rightMost.get() - self.rect.width - 10
            elif self.leftEdge:
                rect.x = 10 + self.rect.width
            else:
                rect.x += self.rect.width / 2
            rect.y += ((iterable - self.maxOptions // 2) + 1) * self.rect.height
        else:
            if self.rightEdge:
                rect.x = self.rightMost.get() - 2 * self.rect.width - 10
            elif self.leftEdge:
                rect.x = 10
            else:
                rect.x -= self.rect.width / 2
            rect.y += (iterable + 1) * self.rect.height
        return rect

    def draw(self, screen):
        firstRect = None
        pygame.draw.rect(screen, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(screen, DARK_BLUE, self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, DARK_BLUE)
        screen.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list[self.scrollPosition:self.scrollPosition + self.maxOptions]):
                rect = self.rect.copy()
                rect = self.getRectPos(rect, i)
                if not i:
                    firstRect = rect.copy()
                pygame.draw.rect(screen,
                                 self.highlight_color if i == self.active_option - self.scrollPosition else self.color,
                                 rect)
                pygame.draw.rect(screen, DARK_BLUE, rect, 1)
                msg = self.font.render(text, 1, DARK_BLUE)
                screen.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                firstRect.x, firstRect.y, self.rect.width * 2, self.rect.height * self.maxOptions // 2)
            pygame.draw.rect(screen, DARK_BLUE, outer_rect, 2)

            if len(self.option_list) > self.maxOptions:
                if self.leftEdge:
                    x = 10 + 2 * self.rect.width
                elif self.rightEdge:
                    x = self.rightMost.get() - 10
                else:
                    x = self.rect.right + self.rect.width / 2
                self.draw_scroll_bar(screen, x)

    def update(self, event_list, surfacePos):
        changeChecker = self.draw_menu
        mousePos = pygame.mouse.get_pos()
        mousePos = (mousePos[0] - surfacePos[0], mousePos[1] - surfacePos[1])
        self.menu_active = self.rect.collidepoint(mousePos)

        self.active_option = -1
        for i in range(self.maxOptions):
            rect = self.rect.copy()
            rect = self.getRectPos(rect, i)
            if rect.collidepoint(mousePos):
                self.active_option = i + self.scrollPosition

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.menu_active:
                        self.draw_menu = not self.draw_menu
                    elif self.draw_menu and self.active_option >= 0:
                        self.selected = self.active_option
                        self.draw_menu = False
                elif event.button == 4:
                    self.scrollPosition = max(0, self.scrollPosition - 1)
                elif event.button == 5:
                    self.scrollPosition = min(len(self.option_list) - self.maxOptions, self.scrollPosition + 1)
        if not self.draw_menu:
            if changeChecker != self.draw_menu:
                return True
        return self.draw_menu

    def updateSizes(self):
        self.rect = pygame.Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
        self.font = pygame.font.SysFont('comicsansms', int(self.fontSize.get()))


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
        self.textPos: list[AutoResizableSet] = [rNums(10, 10, intList=1), rNums(10, 40, intList=1), rNums(10, 60, intList=1), rNums(10, 80, intList=1)]

        self.upgradeButton = NoImgButton(10, 117, 170, 35, LIME_GREEN, LIME_GREEN, LIME_GREEN2, f"", fontSize=18, textColor=WHITE)
        self.targetButton = NoImgButton(10, 155, 170, 35, DARKER_YELLOW, DARKER_YELLOW, YELLOW, f"", fontSize=18, textColor=WHITE)
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
            pygame.draw.rect(self.surface, OPAQUE_LIGHT_BLUE, self.decals[0].get())
            pygame.draw.rect(self.surface, DARK_BLUE, self.decals[1].get())

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
            pass        # NoneType AttributeError

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
