import pygame as pg

class text:
    def __init__(self, x, y, text="", fontSize=32, font=None, colour=(255, 255, 255)):
        self.rect = pg.Rect(x, y, 0, 0)
        self.text = text
        self.font = pg.font.Font(font, fontSize)
        self.colour = colour

    def draw(self, screen):
        wrappedLines = self.text.split("\n")
        maxLineWidth = 0

        for line in wrappedLines:
            textSurface = self.font.render(line, True, self.colour)
            maxLineWidth = max(maxLineWidth, textSurface.get_width())

        for i, line in enumerate(wrappedLines):
            textSurface = self.font.render(line, True, self.colour)
            textRect = textSurface.get_rect()

            textRect.topleft = (self.rect.x, self.rect.y + i * textRect.height)
            screen.blit(textSurface, textRect)

    def centre(self, screen, xOffset=0, yOffset=0):
        wrappedLines = self.text.split("\n")
        maxLineWidth = 0

        for line in wrappedLines:
            textSurface = self.font.render(line, True, self.colour)
            maxLineWidth = max(maxLineWidth, textSurface.get_width())

        totalHeight = len(wrappedLines) * self.font.get_linesize()

        self.rect.width = maxLineWidth
        self.rect.height = totalHeight

        self.rect.x = (screen.get_width() - self.rect.width) // 2 + xOffset
        self.rect.y = (screen.get_height() - self.rect.height) // 2 + yOffset

    def textWrap(self, maxWidth):
        words = self.text.split()
        wrappedText = ""
        currentLine = ""

        for word in words:
            testLine = currentLine + word + " "
            testWidth, _ = self.font.size(testLine)

            if testWidth <= maxWidth:
                currentLine = testLine
            else:
                wrappedText += currentLine + "\n"
                currentLine = word + " "

        wrappedText += currentLine
        self.text = wrappedText.strip()
        self.rect.height = len(wrappedText.split('\n')) * self.font.get_linesize()

    def setText(self, text):
        ALPHABET = "äabcdefghijklmnopqrstuvwxyz1234567890!£$%^&*()-_=+.,<>/?'’@#~:; "
        self.text = "".join(char for char in text if char.lower() in ALPHABET.lower())

class progressBar:
    def __init__(self, x, y, width, height=16, progress=0, maxValue=100, colours=[(255, 255, 255), (25, 25, 25)]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.progress = progress
        self.maxValue = maxValue
        self.colours = colours

    def draw(self, screen):
        pg.draw.rect(screen, self.colours[0], (self.x, self.y, self.width, self.height))

        progressWidth = int(self.width * (self.progress / self.maxValue))
        pg.draw.rect(screen, self.colours[1], (self.x, self.y, progressWidth, self.height))

    def setValue(self, progress):
        self.progress = max(0, min(progress, self.maxValue))