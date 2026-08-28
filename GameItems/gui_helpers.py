from pygame import Surface, font, Color

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
    word_surface: Surface
    for line in words:
        writtenLine = ''
        for word in line:
            if writtenLine:
                writtenLine += f' {word}'
            else:
                writtenLine += word
            if writtenFont.render(writtenLine, True, color).get_width() < max_width:
                word_surface = writtenFont.render(writtenLine, True, color)
            else:
                wordWidth, wordHeight = word_surface.get_size()
                surface.blit(word_surface, ((surface.get_width() - wordWidth) / 2, yPos))
                yPos += wordHeight
                writtenLine = word
                if writtenLine == line[-1]:
                    word_surface = writtenFont.render(writtenLine, True, color)
        wordWidth, wordHeight = word_surface.get_size()
        surface.blit(word_surface, ((surface.get_width() - wordWidth) / 2, yPos))
        yPos += wordHeight
