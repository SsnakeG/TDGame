import math
from random import choice

import pygame.transform
from pygame import font, transform, draw, Surface, mixer
from GameItems.tdColors import *
from GameItems.tdImages import enemyStats, iceImg, fireImg
from GameItems.autoResizableNum import *

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
