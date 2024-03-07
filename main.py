import pygame
from GameItems.objects import Block, NoImgButton, PopupWindow, Button, OptionBox
from GameItems.tdColors import green_elements, BLACK, EMPTY_COLOR
from GameItems.tdImages import background, FPS
from GameItems.AutoResizableNum import *
from random import choice

from GameStates.menu import Menu
from GameStates.options import OptionMenu, LoadOutMenu
from GameStates.mapSelector import MapSelector
from GameStates.trackEditor import TrackEditor
from GameStates.game import Game

pygame.font.init()


def changeAudioVolume(vol, *audio):
    for audio in audio:
        audio.set_volume(vol)


def updateWindowSize(w, h):
    AutoResizableNum.update(w, h)
    sur = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    gameGUI.surface = sur
    for b in NoImgButton.buttons:
        b.updateSizes()
    for b in Button.buttons:
        b.updateSizes()
    for window in PopupWindow.windows:
        window.updateSizes()
    for box in OptionBox.boxes:
        box.updateSizes()
    gameGUI.selectionBox.updateSizes()
    mainMenu.updateSize()
    optionMenu.updateSize()
    loadOutMenu.updateSize()
    mapMenu.updateSize()
    # trackEditor.updateSize()
    gameGUI.updateSize()

    b = pygame.transform.scale(background, (rNum(screen.get_width(), 1).end(), rNum(screen.get_height(), 1).end()))
    return sur, b


SIZE = (600, 600)
backgroundX = rNum(600, 1)
backgroundY = rNum(700, 1)
AutoResizableNum.setupDefaults(*SIZE)
screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
pygame.display.set_caption('Tower Defense')
clock = pygame.time.Clock()

blockSize = rNum(25, 1)
mapDimensions = (600, 600)
blockArray: list[list[Block]] = [[Block([j * blockSize.get(), i * blockSize.get()], choice(green_elements), blockSize.get())
                                  for j in range(int(mapDimensions[1] / blockSize.get()))] for i in range(int(mapDimensions[0] / blockSize.get()))]
trackEditorArray: list[list[Block]] = [[Block([j * 20 + 50, i * 20 + 15], choice(green_elements), blockSize.get())
                                  for j in range(int(mapDimensions[1] / blockSize.get()))] for i in range(int(mapDimensions[0] / blockSize.get()))]

playSpeed = 1

run = True
paused = False
win = False
lose = False

clickAllowed = True

selectedUnit = None
name = "No Tower Selected"
newPage = True

mainMenu = Menu(screen)
optionMenu = OptionMenu(screen)
loadOutMenu = LoadOutMenu(screen)
mapMenu = MapSelector(screen)
trackEditor = TrackEditor(screen)
gameGUI = Game(screen, surface, playSpeed)

menu = True
options = False
loadOutSelector = False
mapSelector = False
game = False
trackEditing = False
num = None

bg = pygame.transform.scale(background, (rNum(screen.get_width(), 1).end(), rNum(screen.get_height(), 1).end()))


if __name__ == '__main__':
    while run:
        num = None
        mouseButton1 = pygame.mouse.get_pressed()[0]
        clicked = mouseButton1 and clickAllowed
        if not mouseButton1:
            clickAllowed = True

        mousePos = pygame.mouse.get_pos()

        events = pygame.event.get()
        for ev in events:
            match ev.type:
                case pygame.QUIT:
                    run = False
                case pygame.VIDEORESIZE:
                    surface, bg = updateWindowSize(ev.w, ev.h)
                case pygame.KEYDOWN:
                    if game:
                        match ev.key:
                            case pygame.K_ESCAPE:
                                paused = not paused
                            case pygame.K_1:
                                num = 0
                            case pygame.K_2:
                                num = 1
                            case pygame.K_3:
                                num = 2
                            case pygame.K_4:
                                num = 3
                            case pygame.K_5:
                                num = 4
                            case pygame.K_6:
                                num = 5
                        if num is not None:
                            name = gameGUI.selectUnitType(mousePos, num)

        size = screen.get_size()
        if size[0] > size[1]:
            x = (screen.get_width()-size[1])/2
            y = 0
        else:
            x = 0
            y = (screen.get_height()-size[0])/2
        screenPos = (x, y)

        screen.fill(BLACK)
        screen.blit(bg, (0, 0))

        if menu:
            mainMenu.draw(mousePos, screenPos)
            menu, options, run, mapSelector, clickAllowed = mainMenu.checkClicks(run, clicked, mousePos, clickAllowed, screenPos)

        elif options:
            if loadOutSelector:
                loadOutMenu.draw(mousePos, screenPos, clickAllowed, events, screenPos)
                loadOutSelector, clickAllowed = loadOutMenu.checkClicks(clicked, clickAllowed)
            else:
                optionMenu.draw(mousePos, screenPos)
                optionMenu.updateSliders(screenPos)
                options, menu, loadOutSelector, clickAllowed = optionMenu.checkClicks(clicked, clickAllowed)
            gameGUI.playSpeed = optionMenu.rgbSlider.getValue()

        elif mapSelector:
            mapMenu.draw(mousePos, screenPos)
            mapSelector, game, name, win, lose, menu, trackEditing, selectedUnit, clickAllowed = \
                mapMenu.checkClicks(clicked, mousePos, clickAllowed, loadOutMenu, screenPos)
            if game:
                gameGUI.selectedMap = mapMenu.selectedMap
                gameGUI.chosenMap = mapMenu.chosenMap
                gameGUI.loadLoadOut(loadOutMenu.loadLoadOut())
                # changeAudioVolume(optionMenu.volumeSlider.getValue(), *audios)

        elif trackEditing:
            run = trackEditor.update(events, mousePos, trackEditorArray)
            trackEditor.checkClicks(clicked, mousePos, trackEditorArray)
            clickAllowed, trackEditing, mapSelector = trackEditor.confirmation(clicked, mousePos, trackEditorArray, clickAllowed, mapMenu)

        elif game:
            menu, game, clickAllowed, name = gameGUI.update(name, blockSize, blockArray, clickAllowed, mousePos, clicked, screenPos)
            clickAllowed, name = gameGUI.checkClicks(clicked, mousePos, blockArray, name, clickAllowed, screenPos)

        surface.fill(EMPTY_COLOR)

        clock.tick(FPS)
        pygame.display.update()
    pygame.quit()
