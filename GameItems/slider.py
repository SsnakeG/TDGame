from GameItems.autoResizableNum import rNum
from pygame import Surface, draw, font, mouse
import math
from GameItems.tdColors import BLUE
from GameItems.gui_helpers import customRound

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
        self.min = 0
        self.max = 1

        self.bgColor = (128, 128, 128)
        self.fgColor = (255, 255, 255)
        self.fillColor = (255, 0, 0)

        self.value = 0
        self.nobScale = 0.35
        self.held = False

        self.interval = 1

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.x = rNum(options["x"], 1)
        self.y = rNum(options["y"], 1)
        self.height = rNum(options["height"], 1)
        self.width = rNum(options["width"], 1)

        self.fontSize = rNum(24, 1)

        self.borderWidth = rNum(int(self.height.initial() * (1 / 3)), 1)
        self.slideXMax = rNum(self.x.initial() + self.width.initial() - self.borderWidth.initial(), 1)
        self.slideXMin = rNum(self.x.initial() + self.borderWidth.initial(), 1)
        self.slideDifference = rNum(self.slideXMax.initial() - self.slideXMin.initial(), 1)

        if self.value <= self.min:
            self.value = self.min
            self.slideX = self.slideXMin.get()
        else:
            self.slideX = self.slideDifference * (self.value / self.max) + self.slideXMin

        Slider.sliders.append(self)

    def checkClickPos(self, offset=(0, 0)):
        mousePos = mouse.get_pos()
        mousePos = (mousePos[0] - offset[0], mousePos[1] - offset[1])
        dist = math.dist(mousePos, (self.slideX, self.y + self.height / 2))
        if dist <= self.height * self.nobScale:
            return True
        return False

    def getValue(self):
        lowValue = self.slideX - self.slideXMin
        percent = lowValue / self.slideDifference
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
        if self.slideX >= self.slideXMax:
            self.slideX = self.slideXMax.get()
        elif self.slideX <= self.slideXMin:
            self.slideX = self.slideXMin.get()
        self.getValue()

    def draw(self, screen: Surface):
        draw.rect(screen, self.bgColor, (self.x.get(), self.y.get(), self.width.get(), self.height.get()))
        draw.rect(screen, (0, 0, 0), (self.x + self.borderWidth, self.y + self.borderWidth,
                                      self.width - 2 * self.borderWidth,
                                      self.height - 2 * self.borderWidth))
        draw.rect(screen, self.fillColor, (
            self.x + self.borderWidth, self.y + self.borderWidth,
            self.slideX - self.x - 2,
            self.height - 2 * self.borderWidth))
        draw.circle(screen, self.fgColor, ((self.slideX, self.y + self.height / 2)),
                    self.height * self.nobScale)

        f = font.SysFont('calibri', int(self.fontSize.get()))
        t = f.render(f"{self.value}", True, BLUE, None)
        screen.blit(t, (self.x.get(), self.y.get()))