import pygame


def red_scale(color, increase: float = 1.1):
    new_color = [color[0] * increase if color[0] * increase < 255 else 255, color[1], color[2]]
    return new_color


def green_scale(color, increase: float = 1.1):
    new_color = [color[0], color[1] * increase if color[1] * increase < 255 else 255, color[2]]
    return new_color


def blue_scale(color, increase: float = 1.1):
    new_color = [color[0], color[1], color[2] * increase if color[2] * increase < 255 else 255]
    return new_color


def allScale(color, rv, bv, gv):
    newColor = [red_scale(color, rv)[0], green_scale(color, gv)[1], blue_scale(color, bv)[2]]
    return newColor


# regular colors
BEIGE = (225, 198, 153)
RED = (255, 0, 0)
PINK = (255, 75, 75)
CYAN = (0, 255, 255)
DARKER_CYAN = (0, 128, 200)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (200, 200, 0)
BRIGHT_YELLOW = (230, 230, 0)
DARKER_YELLOW = (180, 180, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (4, 19, 97)
LIGHTER_BLUE = (32, 74, 129)
ORANGE = (255, 85, 0)
LIME_GREEN = (7, 168, 34)
LIME_GREEN2 = (0, 255, 0)

green_elements = [(34, 139, 34), (0, 128, 0), (0, 100, 0)]

# transparent colors
OPAQUE_LIGHT_BLUE = (79, 118, 195, 150)
OPAQUE_ORANGE = (255, 85, 0, 100)
OPAQUE_CYAN = (0, 255, 255, 65)
OPAQUE_RED = (255, 0, 0, 75)
OPAQUE_YELLOW = (255, 255, 75)
OPAQUE_BLUE = (0, 0, 255, 75)
EMPTY_COLOR = pygame.Color(0, 0, 0, 0)

# def brighten(color, increment):
#     new_color = [color[0] + increment, color[1] + increment, color[2] + increment]

#     for value in new_color:
#         if value > 255:
#             value = 255

#     return new_color

# def darken(color, increment):
#     new_color = [color[0] - increment, color[1] - increment, color[2] - increment]

#     for value in new_color:
#         if value < 0:
#             value = 255

#     return new_color
