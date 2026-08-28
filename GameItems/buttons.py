
from GameItems.autoResizableNum import rNum
from pygame import Surface, transform, draw, font, Rect


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
        self.args = []

        self.buttons.append(self)

    def draw(self, surface: Surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def check_click(self, clicked, mousePos, offset:tuple[int, int]=(0, 0)):
        action = False
        pos = (mousePos[0] - offset[0], mousePos[1] - offset[1])

        if self.rect.collidepoint(pos) and clicked and not self.clicked:
            self.clicked = True
            action = True
        if not clicked:
            self.clicked = False
        return action

    # def checkClick(self, offset=(0, 0)):
    #     pos = (mouse.get_pos()[0] - offset[0], mouse.get_pos()[1] - offset[1])

    #     if self.rect.collidepoint(pos):
    #         if mouse.get_pressed()[0] and not self.clicked:
    #             self.clicked = True
    #             self.command(*self.args)
    #     if not mouse.get_pressed()[0]:
    #         self.clicked = False

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

        self.font = font.SysFont('Cambria', int(self.fontSize.get()))
        self.buttonText = text
        self.text = self.font.render(self.buttonText, True, self.textColor if self.textColor else self.bgColor, None)
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
        self.text = self.font.render(text, True, self.textColor if self.textColor else self.bgColor, None)
        self.tRect = self.text.get_rect()
        self.tRect.center = self.rect.center

    def updateSizes(self):
        self.rect.update(int(self.x.get()), int(self.y.get()), int(self.w.get()), int(self.h.get()))
        self.font = font.SysFont('Cambria', int(self.fontSize.get()))
        self.text = self.font.render(self.buttonText, True, self.textColor if self.textColor else self.bgColor, None)
        self.tRect = self.text.get_rect()
        self.tRect.center = self.rect.center