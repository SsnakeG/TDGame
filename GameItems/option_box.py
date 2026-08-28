from GameItems.autoResizableNum import rNum
from pygame import draw, font, mouse, Rect, MOUSEBUTTONDOWN
from GameItems.tdColors import DARK_BLUE

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
        firstRect: Rect
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