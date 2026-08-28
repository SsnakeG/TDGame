from GameItems.autoResizableNum import rNum
import random
import math
from GameItems.tdImages import enemyStats, fireImg, iceImg
from pygame import mixer, Surface, draw, transform


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
        img = transform.scale(self.image, (self.size.get(), self.size.get()))
        screen.blit(img, (self.location[0].get(), self.location[1].get()))
        draw.rect(screen, (255, 0, 0), [self.location[0].get(), self.location[1].get(), self.size * self.health / self.initial_health, 2])
        if self.fire_status:
            screen.blit(transform.scale(self.fire, (self.size.get(), self.size.get())), (self.location[0].get(), self.location[1].get()))
        if self.ice_status:
            screen.blit(transform.scale(self.ice, (self.size.get(), self.size.get())), (self.location[0].get(), self.location[1].get()))

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

            if self.location[0] > self.targeted_coord[0]:
                self.location[0] = rNum(self.location[0].initial() - self.speed, 3)
            elif self.location[0] < self.targeted_coord[0]:
                self.location[0] = rNum(self.location[0].initial() + self.speed, 3)
            elif self.location[1] > self.targeted_coord[1]:
                self.location[1] = rNum(self.location[1].initial() - self.speed, 3)
            elif self.location[1] < self.targeted_coord[1]:
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
                newEnemy = random.choice(enemyTypes)
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