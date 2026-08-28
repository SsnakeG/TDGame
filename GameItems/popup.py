from GameItems.autoResizableNum import AutoResizableNum, rNum
from pygame import Surface, transform, font
from GameItems.buttons import Button
from GameItems.tdImages import checkImg, xImg
from GameItems.gui_helpers import blitText

class PopupWindow:  # Autoresize check
    windows = []
    x: AutoResizableNum
    y: AutoResizableNum

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
            self.x = rNum(0, 1)
            self.y = rNum(0, 1)

        self.numOfOptions = options["optionNum"]

        self.imageSize = (
            rNum(self.img.get_width() * options["scale"][0], 1), rNum(self.img.get_height() * options["scale"][1], 1))
        self.buttonSize = (75 * options["scale"][0], 75 * options["scale"][1])

        self.image = transform.scale(self.img, (self.imageSize[0].get(), self.imageSize[1].get()))
        self.optionNo: Button
        if self.numOfOptions == 2:
            self.optionYes = Button(self.image.get_width() * (1 / 6), self.image.get_height() * (2 / 3),
                                    transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
            self.optionNo = Button(self.image.get_width() * (7 / 12), self.image.get_height() * (2 / 3),
                                   transform.scale(xImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)
        elif self.numOfOptions == 1:
            self.optionYes = Button(self.image.get_width() * (3 / 8), self.image.get_height() * (2 / 3),
                                    transform.scale(checkImg, (self.buttonSize[0], self.buttonSize[1])), 1, 1)

        self.textColor = options["textColor"]
        self.text = options["text"]

        self.surface = Surface((int(self.imageSize[0].get()), int(self.imageSize[1].get())))

        self.windows.append(self)

    def draw(self, surface: Surface):
        f = font.SysFont('calibri', int(self.fontSize.get()))
        self.surface.blit(self.image, (0, 0))
        blitText(self.surface, self.text, (self.image.get_height() * (1 / 12)), f, color=self.textColor)
        self.optionYes.draw(self.surface)
        if self.optionNo:
            self.optionNo.draw(self.surface)
        if self.centering:
            self.x.end()
            self.y.end()
            self.x = rNum((surface.get_width() - self.image.get_width()) / 2, 1)
            self.y = rNum((surface.get_height() - self.image.get_height()) / 2, 1)
        surface.blit(self.surface, (self.x.get(), self.y.get()))

    def updateSizes(self):
        self.image = transform.scale(self.img, (self.imageSize[0].get(), self.imageSize[1].get()))
        self.surface = Surface((int(self.imageSize[0].get()), int(self.imageSize[1].get())))