from pygame import Surface, transform, mouse, font, Rect, draw, Color, MOUSEBUTTONDOWN
from GameItems.gameEntities import Block, Farm, Tower
from GameItems.tdColors import *
from GameItems.tdImages import xImg, checkImg
import math

from GameItems.autoResizableNum import rNum, rNums, AutoResizableNum, AutoResizableSet


def customRound(num: float, roundedTo: float):
    counter = 0
    while roundedTo < 1:
        num *= 10
        roundedTo *= 10
        counter += 1
    num = round(num)
    num /= 10 ** counter
    return num


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


class Button:  # Autoresize check
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


class NoImgButton:  # Autoresize check
    buttons = []

    def __init__(self, x, y, w, h, bgColor, fgColor, hovColor, text, fontSize=24, command=None, textColor=None):
        self.x, self.y, self.w, self.h = rNum(x, 1), rNum(y, 1), rNum(w, 1), rNum(h, 1)
        self.fontSize = rNum(fontSize, 1)
        self.rect = Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
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

    def draw(self, surface: Surface):
        draw.rect(surface, self.bgColor, self.rect)
        if self.hovering:
            draw.rect(surface, self.hoveredColor,
                      (self.rect.x + 5, self.rect.y + 5, self.rect.w - 10, self.rect.h - 10))
        else:
            draw.rect(surface, self.fgColor,
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


class Map:  # Autoresize check
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
                block = Block((self.location[0].initial() + j * self.miniBlockSize.initial(),
                               self.location[1].initial() + i * self.miniBlockSize.initial()), (0, 128, 0), 5, True)
                self.array[i].append(block)


class MapsPage:  # Autoresize check
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


class Slider:  # Autoresize check
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
        draw.rect(screen, (0, 0, 0), (self.x.get() + self.borderWidth.get(), self.y.get() + self.borderWidth.get(),
                                      self.width.get() - 2 * self.borderWidth.get(),
                                      self.height.get() - 2 * self.borderWidth.get()))
        draw.rect(screen, self.fillColor, (
            self.x.get() + self.borderWidth.get(), self.y.get() + self.borderWidth.get(),
            self.slideX - self.x.get() - 2,
            self.height.get() - 2 * self.borderWidth.get()))
        draw.circle(screen, self.fgColor, (self.slideX, self.y.get() + self.height.get() / 2),
                    self.height.get() * self.nobScale)

        f = font.SysFont('comicsansms', int(self.fontSize.get()))
        t = f.render(f"{self.value}", False, BLUE, None)
        screen.blit(t, (self.x.get(), self.y.get()))


class PopupWindow:  # Autoresize check
    windows = []
    x: AutoResizableNum | int | float
    y: AutoResizableNum | int | float

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

        self.imageSize = (
            rNum(self.img.get_width() * options["scale"][0], 1), rNum(self.img.get_height() * options["scale"][1], 1))
        self.buttonSize = (75 * options["scale"][0], 75 * options["scale"][1])

        self.image = transform.scale(self.img, (self.imageSize[0].get(), self.imageSize[1].get()))
        if self.numOfOptions == 2:
            self.optionYes = Button(self.image.get_width() * (1 / 6), self.image.get_height() * (2 / 3),
                                    transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
            self.optionNo = Button(self.image.get_width() * (7 / 12), self.image.get_height() * (2 / 3),
                                   transform.scale(xImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
        elif self.numOfOptions == 1:
            self.optionYes = Button(self.image.get_width() * (3 / 8), self.image.get_height() * (2 / 3),
                                    transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
            self.optionNo = None

        self.textColor = options["textColor"]
        self.text = options["text"]

        self.surface = Surface((int(self.imageSize[0].get()), int(self.imageSize[1].get())))

        self.windows.append(self)

    def draw(self, surface: Surface):
        f = font.SysFont('comicsansms', int(self.fontSize.get()))
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


class OptionBox:  # Autoresize check
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
        self.rect = Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))
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
        scroll_bar_rect = Rect(x, scroll_bar_y, 10, scroll_bar_height)
        draw.rect(screen, DARK_BLUE, scroll_bar_rect)

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
        draw.rect(screen, self.highlight_color if self.menu_active else self.color, self.rect)
        draw.rect(screen, DARK_BLUE, self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, DARK_BLUE)
        screen.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list[self.scrollPosition:self.scrollPosition + self.maxOptions]):
                rect = self.rect.copy()
                rect = self.getRectPos(rect, i)
                if not i:
                    firstRect = rect.copy()
                draw.rect(screen,
                          self.highlight_color if i == self.active_option - self.scrollPosition else self.color,
                          rect)
                draw.rect(screen, DARK_BLUE, rect, 1)
                msg = self.font.render(text, 1, DARK_BLUE)
                screen.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                firstRect.x, firstRect.y, self.rect.width * 2, self.rect.height * self.maxOptions // 2)
            draw.rect(screen, DARK_BLUE, outer_rect, 2)

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
        mousePos = mouse.get_pos()
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
            if event.type == MOUSEBUTTONDOWN:
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
        self.rect = Rect(self.x.get(), self.y.get(), self.w.get(), self.h.get())
        self.font = font.SysFont('comicsansms', int(self.fontSize.get()))


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
