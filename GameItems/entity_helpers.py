import math
from pygame import font, transform, Surface, mixer

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