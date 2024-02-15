import pygame as pg

def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(value, maximum))

class inputBox:
    def __init__(self, x, y, w=140, h=32, max = 0, prompt="", filled=False, text="", ruleset=""):
        # Initialize input box attributes
        if ruleset:
            self.ruleset = ruleset
        else:
            self.ruleset = "abcdefghijklmnopqrstuvwxyz1234567890!£$%^&*()-_=+.,<>/?'@#~:; "
        self.rect = pg.Rect(x, y, w, h)
        self.colour = (150, 150, 150)
        self.max = max
        self.prompt = prompt
        self.text = text
        self.font = pg.font.Font(None, h)
        self.textSurface = self.font.render(text, True, self.colour)
        self.active = False
        self.hover = False
        self.filled = filled
        self.finalText = "placeholder"

    # Handle events such as mouse clicks and key presses
    def handleEvent(self, event):
        # Mouse events
        modifiedText = ""
        for char in self.text:
            if char not in self.ruleset:
                modifiedText += ""  # Replace with your desired replacement
            else:
                modifiedText += char
        self.text = modifiedText

        if event.type == pg.MOUSEBUTTONDOWN:
            # Check if mouse clicked inside the input box
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            # Change color based on activity
            self.colour = (255, 255, 255) if self.active else (150, 150, 150)
        # Keyboard events
        if event.type == pg.KEYDOWN:
            if self.active:
                # Handle Enter, Backspace, and Ctrl+V for paste
                if event.key == pg.K_RETURN:
                    self.finalText = self.text
                    self.text = ""
                    self.active = False
                    self.colour = (150, 150, 150)
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif (event.key == pg.K_v) and (event.mod & pg.KMOD_CTRL):
                    try:
                        # Try to get text from the clipboard and append it to the input
                        pg.scrap.init()
                        pg.scrap.set_mode(pg.SCRAP_CLIPBOARD)
                        clipboard = pg.scrap.get("text/plain;charset=utf-8").decode()
                        clipboard = ''.join(char for char in clipboard if char.isprintable())
                        self.text += clipboard
                    except:
                        pass
                else:
                    # Handle regular text input
                    if (len(self.text) < self.max or self.max == 0) and event.unicode in self.ruleset:
                        self.text += event.unicode
                        
                # Update the rendered text surface
                self.textSurface = self.font.render(self.text, True, (20, 20, 20))
        # Mouse motion events for hover effect
        elif event.type == pg.MOUSEMOTION and not self.active:
            self.hover = self.rect.collidepoint(event.pos)
            self.colour = (200, 200, 200) if self.hover else (150, 150, 150)

    # Update the input box width based on text width
    def update(self):
        if not self.rect.w > self.max or self.max == 0:
            width = max(200, self.textSurface.get_width() + 10)
            self.rect.w = width

    # Draw the input box on the screen
    def draw(self, screen):
        # Draw filled or unfilled input box and text
        if self.filled:
            pg.draw.rect(screen, self.colour, self.rect)
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
        else:
            screen.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 8))
            pg.draw.rect(screen, self.colour, self.rect, 2)

        # Display prompt if there's no text and a prompt is provided
        if not self.text and self.prompt:
            screen.blit(self.font.render(self.prompt, True, (30, 30, 30)), (self.rect.x + 5, self.rect.y + 8))

class button:
    def __init__(self, x, y, action, w=100, h=100, textures=[], cycle=True, state=0, *args):
        self.position = (x, y)
        self.cycle = cycle

        self.action = action
        if not callable(action):
            raise ValueError("'action' argument must be a callable (function).")

        self.collisionBox = pg.Rect(x, y, w, h)
        self.textures = textures
        self.currentTexture = state
        if not textures:
            self.textures.append(pg.Surface((w, h)))
            self.textures.append(pg.Surface((w, h)))
            self.textures[0].fill((255, 255, 255))
            self.textures[1].fill((122, 122, 122))

        self.args = args
        self.select = False
        self.hover = False

    def handleEvent(self, event):
        # Update "collisionBox" every event.
        self.collisionBox.w = self.textures[self.currentTexture].get_width()
        self.collisionBox.h = self.textures[self.currentTexture].get_height()

        # Handle mouse events.
        if event.type == pg.MOUSEMOTION:
            if self.collisionBox.collidepoint(event.pos):
                self.hover = True
            else:
                self.hover = False
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.collisionBox.collidepoint(event.pos):
                self.select = not self.select
        elif event.type == pg.MOUSEBUTTONUP and self.select and event.button == 1:
            self.action(*self.args)
            self.select = False

            # Cycle through the "textures" list, resetting to 0 if it is at the end.
            if not self.currentTexture + 1 > len(self.textures)-1 and self.cycle:
                self.currentTexture += 1
            else:
                self.currentTexture = 0

    def changeTexture(self):
        if not self.currentTexture + 1 > len(self.textures)-1 and self.cycle:
            self.currentTexture += 1
        else:
            self.currentTexture = 0

    def draw(self, screen):
        screen.blit(self.textures[self.currentTexture], self.position)

class slider:
    def __init__(self, x, y, w=140, h=16, value=0, maxValue=100, textures={}):
        self.coords = (x, y)
        self.rect = pg.Rect(x, y, w, h)
        self.knob = pg.Rect(x, y-h//4, 1.5*h, 1.5*h)

        self.select = False
        self.hover = False

        self.value = clamp(value, 0, maxValue)
        self.maxValue = maxValue

        if not textures:
            self.textures = {
                "Rectangle": self.rect,
                "Knob": self.knob
            }
        else:
            self.textures = textures
            
            self.rect.w = self.textures["Rectangle"].get_width()
            self.rect.h = self.textures["Rectangle"].get_height()

            self.knob.w = 1.5*self.rect.h
            self.knob.h = 1.5*self.rect.h

    def handleEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.select = True
                newValue = clamp(
                    (event.pos[0]-self.rect.x) / self.rect.width * self.maxValue,
                    0,
                    self.maxValue
                )
                self.value = newValue
        elif event.type == pg.MOUSEMOTION:
            if self.select:
                newValue = clamp(
                    (event.pos[0]-self.rect.x) / self.rect.width * self.maxValue,
                    0,
                    self.maxValue
                )
                self.value = newValue
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.select = False

    def draw(self, screen):
        knobX = int(self.value / self.maxValue * self.rect.width - self.knob.w//2)
        knobY = self.rect.centery - self.knob.height//2
        self.knob.topleft = (self.rect.x + knobX - 5, knobY)
        if self.textures == {"Rectangle": self.rect, "Knob": self.knob}:
            pg.draw.rect(screen, (255, 255, 255), self.rect)
            pg.draw.ellipse(screen, (100, 100, 100), self.knob)
        else:
            knobY = self.rect.centery - self.textures["Knob"].get_height()//2
            self.knob.topleft = (self.rect.x + knobX - 5, knobY)
            screen.blit(self.textures["Rectangle"], (self.rect.x, self.rect.y))
            screen.blit(self.textures["Knob"], self.knob.topleft)

class filledSlider:
    def __init__(self, x, y, w=140, h=16, value=0, maxValue=100, textures={}):
        self.coords = (x, y)
        self.rect = pg.Rect(x, y, w, h)
        self.eventPos = [0, 0]

        self.select = False

        self.value = clamp(value, 0, maxValue)
        self.maxValue = maxValue

        if not textures:
            self.textures = {
                "Rectangle": self.rect
            }
        else:
            self.textures = textures
            
            self.rect.w = self.textures["Rectangle"].get_width()
            self.rect.h = self.textures["Rectangle"].get_height()

    def handleEvent(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.eventPos = event.pos
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.select = True
                newValue = clamp(
                    (event.pos[0]-self.rect.x) / self.rect.width * self.maxValue,
                    0,
                    self.maxValue
                )
                self.value = newValue
        elif event.type == pg.MOUSEMOTION:
            if self.select:
                newValue = clamp(
                    (event.pos[0]-self.rect.x) / self.rect.width * self.maxValue,
                    0,
                    self.maxValue
                )
                self.value = newValue
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.select = False

    def draw(self, screen):
        filledWidth = int(self.value / self.maxValue * self.rect.width)
        filledRect = pg.Rect(self.rect.topleft, (filledWidth, self.rect.height))
        
        if self.textures == {"Rectangle": self.rect}:
            pg.draw.rect(screen, (255, 255, 255), filledRect)
        else:
            screen.blit(self.textures["Rectangle"], (self.rect.x, self.rect.y))
            pg.draw.rect(screen, (255, 255, 255), filledRect)

def fileExplorer(mode=0):
    import tkinter as tk
    import tkinter.filedialog

    top = tk.Tk()
    top.withdraw()

    if mode == 0:
        fileName = tkinter.filedialog.askopenfilename(parent=top)
    elif mode == 1:
        fileName = tkinter.filedialog.askdirectory(parent=top)
    else:
        raise ValueError("Invalid mode. Use 0 for file selection or 1 for folder selection.")
        
    top.destroy()
    
    return fileName