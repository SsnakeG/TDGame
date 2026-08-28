from pygame import Surface, draw, transform
from GameItems.autoResizableNum import rNum, rNums
from GameItems.enemy import Enemy
from GameItems.game_square import GameSquare
from GameItems.tdColors import ORANGE, CYAN
from GameItems.entity_helpers import pygameCoordsToImageCoords, createAngleFromOrigin, imageScaleByRatio, rotationMatrix
import math

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

    def __init__(self, towerImage: Surface, pos, upgrade_type, block_size=25, attack_range=3, damage=1, speed=1, frames=60, price=100, special=[], tower_type=None, playSpeed=1):
        """Range in pixels, speed in seconds"""
        block_size = rNum(block_size, 4)
        self.target: Enemy
        self.selectedShotStart = []
        self.shotStartingCoord = None
        self.drawnImg: Surface
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
                            [target.location[0] + target.size / 2, target.location[1] + target.size / 2], self.shotList,
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
                if math.dist((enemy.location[0].get(), enemy.location[1].get()), (target.location[0].get(), target.location[1].get())) <= self.special[0] * self.block_size and enemy.is_on_map:
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

    def sell(self, budget, blocks: list[list[GameSquare]]):
        self.sizeRatio.end()
        self.center.end()
        blocks[int(self.pos.endIdx(1) / self.block_size)][int(self.pos.endIdx(0) / self.block_size.end())].has_tower = False
        budget += self.sell_price
        index = Tower.tower_list.index(self)
        Tower.tower_list.pop(index)
        del self
        return budget

    def draw(self, screen: Surface, color, surface):
        try:
            if self.selected:
                draw.circle(surface, color, (self.pos.getIdx(0) + self.block_size / 2, self.pos.getIdx(1) + self.block_size / 2),
                            self.range * self.block_size)
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
                if distance < self.range * self.block_size and not enemy.fire_status:
                    enemy_distance_list[distance] = enemy
                pass
        elif self.type == 'Freezer':
            for enemy in Enemy.enemy_list:
                distance = math.dist((enemy.location[0].get(), enemy.location[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1)))
                if distance < self.range * self.block_size and not enemy.ice_status:
                    enemy_distance_list[distance] = enemy
        else:
            for enemy in Enemy.enemy_list:
                distance = math.dist((enemy.location[0].get(), enemy.location[1].get()), (self.pos.getIdx(0), self.pos.getIdx(1)))
                if distance < self.range * self.block_size:
                    enemy_distance_list[distance] = enemy
        if self.targeting == 0:  # targeting first
            first: Enemy
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
            strong: Enemy
            for enemy in enemy_distance_list:
                if not strong:
                    strong = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].health > strong.health:
                        strong = enemy_distance_list[enemy]
            self.target = strong
        elif self.targeting == 3:  # targeting weakest
            weak: Enemy
            for enemy in enemy_distance_list:
                if not weak:
                    weak = enemy_distance_list[enemy]
                else:
                    if enemy_distance_list[enemy].health < weak.health:
                        weak = enemy_distance_list[enemy]
            self.target = weak
        elif self.targeting == 4:  # targeting last
            last: Enemy
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
