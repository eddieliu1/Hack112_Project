from cmu_graphics import *
import math
import time


class PetUI:
    def __init__(self, startX, startY):
        self.petX = startX
        self.petY = startY

        # Bounce animation
        self.bounce = 0
        self.bounceSpeed = 6  
        self.bounceHeight = 15   

        # Current mood: 'happy' or 'sad'
        self.mood = 'happy'

        # XP + Leveling System
        self.level = 1
        self.xp = 0
        self.baseXpThreshold = 50
        self.levelScaling = 1.5

        # Unlock order
        self.petLevels = ['blob', 'duck', 'axolotl', 'scotty', 'dragon']
        self.unlockedPets = ['blob']   # Start with blob

        # Current pet
        self.currentPet = 'blob'

        # Pet images as URLs
        self.petImages = {
            'blob': {
                'happy': 'https://i.ibb.co/5gnt1ksh/blob-Happy.png',
                'sad': 'https://i.ibb.co/TBBjQDtB/blobSad.png'
            },
            'duck': {
                'happy': 'https://i.ibb.co/zTVFRzRF/duck-Happy.png',
                'sad': 'https://i.ibb.co/FL9Dpjh5/duckSad.png'
            },
            'axolotl': {
                'happy': 'https://i.ibb.co/PvtRK3c3/axolotl-Happy.png',
                'sad': 'https://i.ibb.co/SDj1T97g/axolotl-Sad.png'
            },
            'scotty': {
                'happy': 'https://i.ibb.co/MxNqD9d3/scotty-Happy.png',
                'sad': 'https://i.ibb.co/WW91JX1T/scotty-Sad.png'
            },
            'dragon': {
                'happy': 'https://i.ibb.co/hJg0J4CP/dragon-Happy.png',
                'sad': 'https://i.ibb.co/VYxbQYKZ/dragon-Sad.png'
            }
        }

    # -----------------------
    # Animation
    # -----------------------
    def animateBounce(self):
        t = time.time() * self.bounceSpeed
        self.bounce = math.sin(t) * self.bounceHeight

    # -----------------------
    # XP / Leveling
    # -----------------------
    def xpThreshold(self):
        return self.baseXpThreshold * (self.levelScaling ** (self.level - 1))

    def gainXp(self, amount):
        self.xp += amount

        # Level up automatically
        while self.xp >= self.xpThreshold():
            self.xp -= self.xpThreshold()
            self.level += 1
            self.unlockNextPet()

    def unlockNextPet(self):
        if self.level - 1 < len(self.petLevels):
            petToUnlock = self.petLevels[self.level - 1]
            if petToUnlock not in self.unlockedPets:
                self.unlockedPets.append(petToUnlock)

    def cyclePet(self, direction):
        idx = self.unlockedPets.index(self.currentPet)
        idx = (idx + direction) % len(self.unlockedPets)
        self.currentPet = self.unlockedPets[idx]

    # -----------------------
    # Drawing
    # -----------------------
    def drawXpBar(self):
        barWidth = 300
        barHeight = 20
        x = (600 - barWidth) / 2
        y = 410

        # Background bar
        drawRect(x, y, barWidth, barHeight, fill='lightGray')

        # Fill bar
        fillWidth = (self.xp / self.xpThreshold()) * barWidth

         # Prevent CMU Graphics crash when width == 0
        if fillWidth <= 0:
            fillWidth = 0.001

        drawRect(x, y, fillWidth, barHeight, fill='yellow')

        drawLabel(
            f'Level {self.level}',
            300, y - 15,
            size=18
        )

    def drawPet(self):
        self.animateBounce()
        imgUrl = self.petImages[self.currentPet][self.mood]

        petWidth = 120
        petHeight = 120

        drawImage(
            imgUrl,
            self.petX - petWidth/2,
            self.petY - self.bounce - petHeight/2,
            width=petWidth,
            height=petHeight
        )

        # Show arrows only if there's more than one unlocked pet
        if len(self.unlockedPets) > 1:
            # Left arrow
            drawPolygon(
                self.petX - 100, self.petY,
                self.petX - 85, self.petY - 15,
                self.petX - 85, self.petY + 15,
                fill='gray'
            )
            # Right arrow
            drawPolygon(
                self.petX + 100, self.petY,
                self.petX + 85, self.petY - 15,
                self.petX + 85, self.petY + 15,
                fill='gray'
            )


# ------------------ App Functions ------------------
def onAppStart(app):
    app.width = 600
    app.height = 450
    app.petUI = PetUI(app.width/2, app.height/2)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='lightCyan')

    # Draw pet + XP bar
    app.petUI.drawPet()
    app.petUI.drawXpBar()

    # Instructions (temp)
    drawLabel("Press G = Happy, B = Sad", 300, 30, size=18)
    drawLabel("Press ← / → to switch unlocked pets", 300, 55, size=16)
    drawLabel("Press U to gain XP (test leveling)", 300, 80, size=14)

def onKeyPress(app, key):
    ui = app.petUI

    # Mood keys
    if key == 'g': ui.mood = 'happy'
    if key == 'b': ui.mood = 'sad'

    # XP test key (for now)
    if key == 'u': ui.gainXp(25)

    # Pet cycling via arrows
    if key == 'left': ui.cyclePet(-1)
    if key == 'right': ui.cyclePet(1)

runApp()
