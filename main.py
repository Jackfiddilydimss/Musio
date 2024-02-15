import pygame as pg
import os
import json
import random
import eyed3
from mutagen.mp3 import MP3
from datetime import datetime

import ioSTD.input as input
import ioSTD.output as output

# Version 0.0.1 - Peak of 10% CPU
# Version 0.0.2 - Peak of 0.3% CPU under normal usage
#               - When dragging progress bar, it goes up to 12%
# Version 0.0.3 - Added Song ID picker
#               - Added left/right arrow to skip time, a/d to skip song

def newLog(log, code=-1):
    print(log)
    time = datetime.now().time()
    time = time.strftime('%H:%M:%S')

    with open("./sysLog.txt", "a") as logFile:
        logFile.write(f"{time}: {log}\n")

    if code != -1:
        newLog(f"Quitting with code {code}.")
        exit(code)

if os.stat("./config.json").st_size < 123:
    with open("./defaultCFG.txt", "r") as default:
        defaultCFG = json.loads(default.read())
    
    with open("./config.json", "w") as configFile:
        json.dump(defaultCFG, configFile, indent=4)

    newLog("CFG failed to load. It has been reset.")

# So that more screens can be created at will, I made a class for them.
class screen:
    def __init__(self, elements=[]):
        self.elements = elements

    def setElements(self, elements):
        if type(elements) != list:
            newLog("ERROR: 'ELEMENTS' ARGUMENT IS NOT A LIST.")
        else:
            self.elements = elements
            newLog("New elements loaded.")

    def handleEvent(self, event):
        for element in self.elements:
            if hasattr(element, 'handleEvent') and callable(getattr(element, 'handleEvent')):
                element.handleEvent(event)

    def draw(self):
        for element in self.elements:
            if hasattr(element, 'draw') and callable(getattr(element, 'draw')):
                element.draw(sc)

# Set up the log by clearing it and creating a function to write to it.
with open("./sysLog.txt", "w") as clear:
    clear.write("")

newLog("Initialising...")
pg.init()
pg.mixer.init()

clock = pg.time.Clock()

resolution = (350, 566)
sc = pg.display.set_mode(resolution)
pg.display.set_caption("Musio")
pg.display.set_icon(pg.image.load("./appIcon.png"))

# Unpack config.json.
newLog("Unpacking 'config.json'...")
cfg = {}
with open("./config.json", "r") as configFile:
    cfg = configFile.read()
    cfg = json.loads(cfg)

playlist = os.listdir(cfg["playlists"]["main"])
for i, song in enumerate(playlist):
    playlist[i] = os.path.join(cfg["playlists"]["main"], song)
if cfg["shuffle"]:
    playlist = cfg["shuffledList"]

if cfg["debug"]:
    import cProfile

    profiler = cProfile.Profile()
    profiler.enable()

# ---- Music Utilities ---- #
def playSong(song):
    global songLen, offset

    offset = 0
    songName = os.path.splitext(os.path.basename(song))[0]
    newLog(f"Playing: {songName}")
    try:
        pg.mixer.music.load(song)
        songLen = pg.mixer.Sound(song).get_length() * 1000
        pg.mixer.music.play()
    except Exception as e:
        newLog(e)
        skip()

    audioFile = eyed3.load(playlist[cfg["songID"]])

    songLengthTxt.setText(str(convertTime(songLen)))
    songIDTxt.setText(f"Song ID: {str(cfg['songID'])}")

    songNameTxt.setText(songName)
    songNameTxt.textWrap(resolution[0]-20)
    songNameTxt.centre(sc, yOffset=-80)

    if audioFile.tag.artist:
        artist = audioFile.tag.artist
    else:
        artist = "Artist not found."
    artistNameTxt.setText(artist)
    artistNameTxt.textWrap(resolution[0]-20)
    artistNameTxt.centre(sc, yOffset=-38)

def skip(inc=1):
    oldID = cfg["songID"]
    cfg["songID"] += inc

    if cfg["loopType"] == 2:
        cfg["songID"] = oldID

    #Loop states:
        # 0 - No loop
        # 1 - Loop normally
        # 2 - Loop one song

    try:
        if cfg["songID"] >= len(playlist):
            newLog("Song ID overflow, looping...")
            if cfg["loopType"] == 0:
                cfg["songID"] = oldID
                pg.mixer.music.stop()
            elif cfg["loopType"] == 1:
                cfg["songID"] = 0
                playSong(playlist[cfg["songID"]])
        elif cfg["songID"] < 0:
            if cfg["loopType"] == 0:
                cfg["songID"] = 0
            elif cfg["loopType"] == 1:
                cfg["songID"] = len(playlist)-1
            playSong(playlist[cfg["songID"]])
        else:
            playSong(playlist[cfg["songID"]])
    except:
        newLog("Playlist not found.", 2)

def pauseToggle():
    cfg["paused"] = not cfg["paused"]
    if cfg["paused"]:
        pg.mixer.music.pause()
    else:
        pg.mixer.music.unpause()

def shuffleToggle():
    global playlist
    try:
        currentSong = playlist[cfg["songID"]]
    except:
        newLog("FATAL ERROR: SONG NOT FOUND", 2)
    cfg["shuffle"] = not cfg["shuffle"]
    if cfg["shuffle"]:
        random.shuffle(playlist)
        cfg["shuffledList"] = playlist
    else:
        try:
            playlist = os.listdir(cfg["playlists"]["main"])
            for i, song in enumerate(playlist):
                playlist[i] = os.path.join(cfg["playlists"]["main"], song)
        except FileNotFoundError:
            newLog("FATAL ERROR: FILE NOT FOUND", 2)
    
    # This is such an inefficient searching algorithm, I am sorry.
    # However, it makes sure that, when shuffling, the songID remains accurate.
    for i, song in enumerate(playlist):
        if song == currentSong:
            cfg["songID"] = i

def loopCycle():
    cfg["loopType"] += 1
    if cfg["loopType"] > 2:
        cfg["loopType"] = 0

def convertTime(ms):
    totalSeconds = ms / 1000

    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = totalSeconds % 60

    formattedTime = "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
    return formattedTime

loadSettings = False
def settingsMenu():
    global loadSettings
    loadSettings = not loadSettings

file = cfg["playlists"]["main"]
def getFileInput(mode):
    global file
    file = input.fileExplorer(mode)
    newLog(file)

# ---- UI setup ---- #
icons = {
    "back": ".\icons/backArrow.png",
    "paused": ".\icons/paused.png",
    "unpaused": ".\icons/unpaused.png",
    "forward": ".\icons/forwardArrow.png",
    "loop": ".\icons/loop.png",
    "notLoop": ".\icons/notLoop.png",
    "loopOne": ".\icons/loopOne.png",
    "shuffle": ".\icons/shuffle.png",
    "notShuffle": ".\icons/notShuffle.png",
    "settings": ".\icons/settingsCog.png",
    "playlistView": ".\icons/playlistView.png"
}
icons = {name: pg.transform.scale(pg.image.load(path), (50, 50)) for name, path in icons.items()}

versionNumber = output.text(0, 0, "Musio 0.0.2", 16)
settingsCog = input.button(resolution[0]-50, 0, settingsMenu, textures=[icons["settings"]], cycle=False)

sharedUI = [versionNumber, 
            settingsCog]

backButton = input.button(resolution[0]//2 - resolution[0]//3 - 25, resolution[1]-resolution[1]//5, skip, 100, 100, [icons["back"]], False, 0, -1)
pauseButton = input.button(resolution[0]//2 - 25, resolution[1]-resolution[1]//5, pauseToggle, textures=[icons["paused"], icons["unpaused"]], state=int(cfg["paused"]))
forwardButton = input.button(resolution[0]//2 + resolution[0]//3 - 25, resolution[1]-resolution[1]//5, skip, textures=[icons["forward"]], cycle=False)
shuffleButton = input.button(forwardButton.position[0] - 50, resolution[1]-resolution[1]//3-55, shuffleToggle, textures=[icons["notShuffle"], icons["shuffle"]], state=int(cfg["shuffle"]))
loopButton = input.button(resolution[0]-60, resolution[1]-resolution[1]//3-55, loopCycle, textures=[icons["notLoop"], icons["loop"], icons["loopOne"]], state=cfg["loopType"])

songProgressBar = input.filledSlider(0, resolution[1]-resolution[1]//3, resolution[0])
songProgressTxt = output.text(2, resolution[1]-resolution[1]//3+16, "00:00:00", 16)
songLengthTxt = output.text(resolution[0]-48, resolution[1]-resolution[1]//3+16, "00:00:00", 16)

songNameTxt = output.text(0, 0, "NO SONG LOADED", 48)
artistNameTxt = output.text(0, 0, "Artist Name Not Found", 16)

volumeSlider = input.slider(0, resolution[1]-resolution[1]//3-17, 100, 8, cfg["volume"])
volumeTxt = output.text(0, resolution[1]-resolution[1]//3-30, "Volume: 100", 16)

setSongInput = input.inputBox(0, 100, filled=True, prompt="Input SongID", ruleset="0123456789")

mainScreen = screen([backButton, 
                     pauseButton, 
                     forwardButton, 
                     shuffleButton, 
                     loopButton, 
                     songNameTxt, 
                     artistNameTxt, 
                     songProgressBar, 
                     songProgressTxt, 
                     songLengthTxt,
                     volumeSlider, 
                     volumeTxt,
                     setSongInput])

currentPlaylistText1 = output.text(6, 6, "Current Playlist:")
currentPlaylistText2 = output.text(6, 32, str(cfg["playlists"]["main"]))
playlistSelectPrompt = output.text(8, 64, "Select a Folder", colour=(0, 0, 0))
playlistSelect = input.button(6, 64, getFileInput, 170, 22, [], False, 0, 1)
settings = screen([currentPlaylistText1, 
                   currentPlaylistText2, 
                   playlistSelect, 
                   playlistSelectPrompt])

currentScreen = mainScreen

songIDTxt = output.text(0, 16, "Song ID: N/A", 16)
if cfg["debug"]:
    playlistMSG = ", \n".join([os.path.splitext(os.path.basename(file_path))[0] for file_path in playlist])
    newLog(playlistMSG)

# ---- Main Loop ---- #
running = True
pressedKeys = set()

newLog("---- Initialised ----")
try:
    playSong(playlist[cfg["songID"]])
except:
    cfg["songID"] = 0
    playSong(playlist[0])

if cfg["paused"]:
    pg.mixer.music.pause()

volumeTxt.setText(f"Volume: {round(volumeSlider.value)}")
pg.mixer.music.set_volume(cfg["volume"]/100)

offset = 0
while running:
    currentPos = pg.mixer.music.get_pos()
    actualPosition = currentPos + offset
    percentage = (actualPosition/songLen)*100
    songProgressBar.value = percentage

    if actualPosition < 0 and percentage < 0:
        skip(0)

    for event in pg.event.get():
        sharedUI[1].handleEvent(event)
        currentScreen.handleEvent(event)
        if loadSettings:
            settings.handleEvent(event)

        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pauseToggle()
                pauseButton.changeTexture()
            elif event.key == pg.K_RETURN:
                oldID = cfg["songID"]
                cfg["songID"] = int(setSongInput.finalText)

                try:
                    playSong(playlist[cfg["songID"]])
                except IndexError:
                    playSong(playSong[oldID])
                    cfg["songID"] = oldID
            elif event.key == pg.K_a:
                skip(-1)
            elif event.key == pg.K_d:
                skip()
            elif event.key == pg.K_LEFT:
                offset -= 10000
                actualPosition = currentPos + offset
                songProgressBar.value = (actualPosition/songLen)*100
            elif event.key == pg.K_RIGHT:
                offset += 10000
                actualPosition = currentPos + offset
                songProgressBar.value = (actualPosition/songLen)*100

    if songProgressBar.value != percentage:
        offset = ((songProgressBar.value/100)*songLen)
        pg.mixer.music.stop()
        pg.mixer.music.play(0, ((songProgressBar.value/100)*songLen)/1000)

    actualPosition = currentPos + offset
    percentage = (actualPosition/songLen)*100
    songProgressBar.value = percentage

    # Some logic was moved because the app was taking 20% of my CPU up
    songProgressTxt.setText(str(convertTime(actualPosition)))

    if cfg["volume"] != round(volumeSlider.value, 2):
        cfg["volume"] = round(volumeSlider.value, 2)
        volumeTxt.setText(f"Volume: {round(volumeSlider.value)}")

        pg.mixer.music.set_volume(cfg["volume"]/100)

    sc.fill((0, 0, 0))

    currentScreen.draw()

    if loadSettings:
        SETTINGSBG = pg.Surface((resolution[0]-10, resolution[0]-10))
        SETTINGSBG.fill((50, 50, 50))
        sc.blit(SETTINGSBG, (5, 5))
        currentPlaylistText2.text = str(file)

        settings.draw()

        if cfg["playlists"]["main"] != file:
            cfg["songID"] = 0
            cfg["playlists"]["main"] = file
            shuffleToggle()
            shuffleToggle()

        
    if cfg["debug"]:
        songIDTxt.draw(sc)
    for element in sharedUI:
        element.draw(sc)

    if not pg.mixer.music.get_busy() and not cfg["paused"]:
        skip(1)

    pg.display.flip()
    clock.tick(30)
pg.quit()

newLog("Saving 'config.json'...")
print(cfg["volume"])
with open("./config.json", "w") as configFile:
    json.dump(cfg, configFile, indent=4)

if cfg["debug"]:
    profiler.disable()
    profiler.print_stats(sort="cumulative")
    profiler.dump_stats('profile_results.prof')