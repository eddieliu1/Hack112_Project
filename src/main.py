from cmu_graphics import *
import cv2
import mediapipe as mp
from PIL import Image
import math
import time
import json
import os

# --------- persistent storage for max time ---------
MAX_TIME_FILE = "max_posture_time.txt"

def loadMaxTime():
    try:
        with open(MAX_TIME_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return 0.0

def saveMaxTime(value):
    with open(MAX_TIME_FILE, "w") as f:
        f.write(str(value))

# ---------------- user & leaderboard storage ----------------
USER_DIR = 'users'
LEADERBOARD_FILE = "leaderboard.json"

def loadUser(username):
    path = f"{USER_DIR}/{username}.json"
    if not os.path.exists(path):
        return {
            "maxGoodPostureTime": 0.0,
            "totalGoodTime": 0.0,
            "totalBadTime": 0.0,
            "totalSessionTime": 0.0,
            "slouchEvents": 0
        }
    with open(path, "r") as f:
        return json.load(f)

def saveUser(username, data):
    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)
    path = f"{USER_DIR}/{username}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def loadLeaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        return json.load(f)

def saveLeaderboard(lb):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)

def updateLeaderboard(username, score):
    lb = loadLeaderboard()
    found = False
    for entry in lb:
        if entry["username"] == username:
            entry["score"] = max(entry["score"], score)
            found = True
            break
    if not found:
        lb.append({"username": username, "score": score})
    lb.sort(key=lambda x: x["score"], reverse=True)
    saveLeaderboard(lb)

# ---------------------------------------------------
# Pet UI
# ---------------------------------------------------

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
        self.baseXpThreshold = 20   # demo: easier to level
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

    # Animation
    def animateBounce(self):
        t = time.time() * self.bounceSpeed
        self.bounce = math.sin(t) * self.bounceHeight

    # XP / Leveling
    def xpThreshold(self):
        return self.baseXpThreshold * (self.levelScaling ** (self.level - 1))

    def gainXp(self, amount):
        self.xp += amount
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

    # Drawing
    def drawXpBar(self, app):
        # switch to line mode when tiny
        if app.width < 260 or app.height < 160:
            # tiny line at bottom
            lineY = app.height - 30
            lineX0 = app.width * 0.15
            lineX1 = app.width * 0.85
            drawLine(lineX0, lineY, lineX1, lineY, lineWidth=6, fill='lightGray')
            t = self.xp / self.xpThreshold()
            t = max(0, min(1, t))
            fillX1 = lineX0 + t * (lineX1 - lineX0)
            drawLine(lineX0, lineY, fillX1, lineY, lineWidth=6, fill='yellow')
        else:
            barWidth = min(300, app.width - 40)
            barHeight = 20
            x = (app.width - barWidth) / 2
            y = app.height - 40
            drawRect(x, y, barWidth, barHeight, fill='lightGray')
            fillWidth = (self.xp / self.xpThreshold()) * barWidth
            if fillWidth <= 0:
                fillWidth = 0.001
            drawRect(x, y, fillWidth, barHeight, fill='yellow')

        drawLabel(f'Level {self.level}', app.width/2, app.height - 60, size=18)

    def drawPet(self, app):
        self.animateBounce()
        imgUrl = self.petImages[self.currentPet][self.mood]
        maxPetSize = min(120, app.width * 0.5, app.height * 0.5)
        petWidth = maxPetSize
        petHeight = maxPetSize
        drawImage(
            imgUrl,
            self.petX - petWidth/2,
            self.petY - self.bounce - petHeight/2,
            width=petWidth,
            height=petHeight
        )

# ---------------------------------------------------
# App start
# ---------------------------------------------------

def onAppStart(app):
    # camera + pose
    app.cap = cv2.VideoCapture(0)
    app.modes = ['vid', 'pet', 'timer', 'gradient', 'settings']
    app.modeIndex = 0
    app.mode = app.modes[app.modeIndex]

    # base sizes for modes
    app.smallWidth, app.smallHeight = 160, 130
    app.settingsWidth, app.settingsHeight = 500, 500
    app.petWidth, app.petHeight = 600, 450   # IMPORTANT: defined here

    app.constant = None
    app.imageSizeX, app.imageSizeY = app.width//3, app.height//3
    app.mp_pose = mp.solutions.pose
    app.pose = app.mp_pose.Pose(min_detection_confidence=0.5)

    # posture + camera state
    app.goodPosture = True
    app.postureColor = (0, 255, 0)
    app.stepsPerSecond = 10
    app.frame = None
    app.landmarks = None

    # streak timer state
    app.goodPostureTime = 0.0
    app.badPostureTime = 0.0
    app.maxGoodPostureTime = loadMaxTime()

    # analytics
    app.totalSessionTime = 0.0
    app.totalGoodTime = 0.0
    app.totalBadTime = 0.0
    app.slouchEvents = 0
    app.prevGoodPosture = True

    # focus info
    app.showFocusInfo = False
    app.focusHistory = []
    app.focusSampleTime = 0.0

    # Pet
    app.petUI = PetUI(app.width/2, app.height/2)

    # ---------- LOGIN / MENU state ----------
    app.loginState = 'login'      # 'login', 'menu', 'tracking', 'leaderboard'
    app.usernameInput = ''
    app.currentUser = None
    app.userData = None
    app.loginMessage = "Type a username (alphanumeric) and press Enter"


# ---------- posture + color helpers ----------

def getPostureColor(app, landmarks):
    if app.constant is None:
        return (0, 255, 0)
    leftShoulder = landmarks[11]
    rightShoulder = landmarks[12]
    nose = landmarks[0]
    shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
    headForwardMagnitude = app.constant + nose.y - shoulderMidY
    threshold = 0.10
    t = headForwardMagnitude / threshold
    t = max(0, min(1, t))
    r = int(t * 255)
    g = int((1 - t) * 255)
    b = 0
    return (r, g, b)

def checkPosture(app, landmarks):
    leftShoulder = landmarks[11]
    rightShoulder = landmarks[12]
    nose = landmarks[0]
    shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
    threshold = app.constant if app.constant is not None else 0.05
    headForward = nose.y > shoulderMidY - threshold
    return not headForward

def resetWindowSize(app):
    # Reset window size to default for the current mode
    if app.mode == 'settings':
        app.width, app.height = app.settingsWidth, app.settingsHeight
    elif app.mode == 'vid':
        app.width, app.height = app.petWidth, app.petHeight
    elif app.mode == 'pet':
        app.width, app.height = app.petWidth, app.petHeight
    else:
        app.width, app.height = app.smallWidth, app.smallHeight

def updateMaxRuntime(app):
    dt = 1 / app.stepsPerSecond

    app.totalSessionTime += dt
    if app.goodPosture:
        app.totalGoodTime += dt
    else:
        app.totalBadTime += dt

    if app.goodPosture:
        if app.badPostureTime > 0:
            app.badPostureTime = 0.0
            resetWindowSize(app)
        app.goodPostureTime += dt
        if app.goodPostureTime > app.maxGoodPostureTime:
            app.maxGoodPostureTime = app.goodPostureTime
            saveMaxTime(app.maxGoodPostureTime)
    else:
        app.goodPostureTime = 0.0
        app.badPostureTime += dt
        if app.badPostureTime > 7 and app.mode == 'timer':
            grow = max(1, int(30 / app.stepsPerSecond))
            app.width  += grow
            app.height += grow

    # Pet XP
    if hasattr(app, 'petUI'):
        if app.goodPosture:
            app.petUI.gainXp(dt)
            app.petUI.mood = 'happy'
        else:
            app.petUI.mood = 'sad'

# ---------- focus score helpers ----------

def computeFocusScore(app):
    if app.totalSessionTime < 10:
        return None
    goodPct = 100 * app.totalGoodTime / app.totalSessionTime
    streakSec = app.maxGoodPostureTime
    streakScore = min(streakSec, 60) / 60 * 100
    slouches = app.slouchEvents
    stabilityScore = max(0, 100 * (1 - slouches / 10))
    score = 0.5 * goodPct + 0.3 * streakScore + 0.2 * stabilityScore
    return max(0, min(100, score))

def getFocusEstimate(app):
    score = computeFocusScore(app)
    if score is None:
        return "Not enough data"
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"

# ---------- saving current user ----------

def saveCurrentUserData(app):
    if app.currentUser is None or app.userData is None:
        return
    app.userData["maxGoodPostureTime"] = app.maxGoodPostureTime
    app.userData["totalGoodTime"] = app.totalGoodTime
    app.userData["totalBadTime"] = app.totalBadTime
    app.userData["totalSessionTime"] = app.totalSessionTime
    app.userData["slouchEvents"] = app.slouchEvents
    saveUser(app.currentUser, app.userData)
    updateLeaderboard(app.currentUser, app.maxGoodPostureTime)

# ---------- events ----------

def onKeyPress(app, key):
    # ----- LOGIN -----
    if app.loginState == "login":
        if key == "enter" and len(app.usernameInput) > 0:
            app.currentUser = app.usernameInput
            app.userData = loadUser(app.currentUser)
            app.maxGoodPostureTime = app.userData.get("maxGoodPostureTime", app.maxGoodPostureTime)
            app.totalGoodTime = app.userData.get("totalGoodTime", app.totalGoodTime)
            app.totalBadTime = app.userData.get("totalBadTime", app.totalBadTime)
            app.totalSessionTime = app.userData.get("totalSessionTime", app.totalSessionTime)
            app.slouchEvents = app.userData.get("slouchEvents", app.slouchEvents)
            app.loginState = "menu"
            return
        elif key == "backspace":
            app.usernameInput = app.usernameInput[:-1]
            return
        elif len(key) == 1 and key.isalnum():
            if len(app.usernameInput) < 20:
                app.usernameInput += key
            return

    # ----- MENU -----
    if app.loginState == "menu":
        if key == "1":
            app.loginState = "tracking"
            resetWindowSize(app)
            return
        elif key == "2":
            app.loginState = "leaderboard"
            return
        elif key == "3":
            saveCurrentUserData(app)
            app.currentUser = None
            app.userData = None
            app.usernameInput = ''
            app.loginState = "login"
            return

    # ----- LEADERBOARD -----
    if app.loginState == "leaderboard":
        app.loginState = "menu"
        return

    # ----- TRACKING CONTROLS -----
    if app.loginState == "tracking":
        # Pet-specific controls
        if app.mode == 'pet':
            ui = app.petUI
            if key == 'u':
                ui.gainXp(25)
                return
            if key == 'a':
                ui.cyclePet(-1)
                return
            if key == 'd':
                ui.cyclePet(1)
                return

        # posture + modes
        if key == 'c' and app.landmarks:
            leftShoulder = app.landmarks[11]
            rightShoulder = app.landmarks[12]
            nose = app.landmarks[0]
            shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2
            app.constant = shoulderMidY - nose.y
            print(f"Baseline captured! Constant: {app.constant:.4f}")
            return

        elif key == 'right':
            app.modeIndex = (app.modeIndex + 1) % len(app.modes)
            app.mode = app.modes[app.modeIndex]
            resetWindowSize(app)
            return

        elif key == 'left':
            app.modeIndex = (app.modeIndex - 1) % len(app.modes)
            app.mode = app.modes[app.modeIndex]
            resetWindowSize(app)
            return

        elif key == 'i' and app.mode == 'settings':
            app.showFocusInfo = not app.showFocusInfo
            return

        elif key == 'q':
            saveCurrentUserData(app)
            onAppStop(app)
            return

def onStep(app):
    # only process camera when tracking
    if app.loginState != "tracking":
        return

    ret, frame = app.cap.read()
    if not ret or frame is None:
        return
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = app.pose.process(rgb_frame)
    app.frame = Image.fromarray(rgb_frame)

    if results.pose_landmarks:
        app.landmarks = results.pose_landmarks.landmark
    else:
        app.landmarks = None
    
    if app.landmarks:
        app.goodPosture = checkPosture(app, app.landmarks)
        app.postureColor = getPostureColor(app, app.landmarks)
    else:
        app.goodPosture = False

    if app.prevGoodPosture and (not app.goodPosture):
        app.slouchEvents += 1
    app.prevGoodPosture = app.goodPosture

    updateMaxRuntime(app)

    dt = 1 / app.stepsPerSecond
    app.focusSampleTime += dt
    if app.focusSampleTime >= 1.0:
        score = computeFocusScore(app)
        if score is not None:
            app.focusHistory.append(score)
        app.focusSampleTime = 0.0

# ---------- drawing ----------

def drawVideo(app):
    if app.frame:
        drawImage(CMUImage(app.frame), 0, 0, width=app.width, height=app.height)
    if app.landmarks:
        drawPoseSkeleton(app, app.landmarks)
    if app.constant is not None:
        drawLabel("Baseline Set", app.width/2, 15, size=10, fill='yellow', bold=True)
    else:
        drawLabel("Press 'C' to set baseline", app.width/2, 15, size=10, fill='white')

def drawTimer(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    if app.goodPosture:
        timerColor = 'green'
        value = app.goodPostureTime
    else:
        timerColor = 'red'
        value = app.badPostureTime
    drawLabel(f"{value:0.1f}s", app.width/2, app.height/2,
              size=40, fill=timerColor, bold=True)
    drawLabel(f"Max: {app.maxGoodPostureTime:0.1f}s",
              app.width - 5, app.height - 5,
              size=14, fill='white', align='right')
    drawLabel("← / → to change mode",
              app.width/2, 15, size=10, fill='white')

def drawGradient(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(*app.postureColor))

def drawPetMode(app):
    # just draw – do NOT write to app.petWidth / app.petHeight here
    drawRect(0, 0, app.width, app.height, fill='lightCyan')

    app.petUI.petX = app.width / 2
    if app.height > 260:
        app.petUI.petY = app.height / 2 + 10
    else:
        app.petUI.petY = app.height / 2

    app.petUI.drawPet(app)
    app.petUI.drawXpBar(app)

    # Only show text if enough room
    if app.width >= 450 and app.height >= 200:
        drawLabel("Good posture = XP (1 XP/sec)", app.width/2, 30, size=18)
        drawLabel("Earn XP to level up and unlock new pets", app.width/2, 55, size=16)
        drawLabel("A / D to switch pets   •   ← / → change mode",
                  app.width/2, 80, size=14)


def onResize(app):
    # remember per-mode default sizes when user resizes
    if hasattr(app, 'loginState') and app.loginState != 'tracking':
        return
    if app.mode == 'pet':
        app.petWidth, app.petHeight = app.width, app.height
    elif app.mode == 'settings':
        app.settingsWidth, app.settingsHeight = app.width, app.height
    else:
        app.smallWidth, app.smallHeight = app.width, app.height


def drawSettings(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    focusLabel = getFocusEstimate(app)
    if app.totalSessionTime > 0:
        goodPct = 100 * app.totalGoodTime / app.totalSessionTime
        badPct  = 100 * app.totalBadTime  / app.totalSessionTime
    else:
        goodPct = badPct = 0.0

    if not app.showFocusInfo:
        drawLabel("Focus Report (Posture-Based)", app.width/2, 50,
                  size=22, fill='white', bold=True)
        y = 110; dy = 30
        drawLabel(f"Total session time: {app.totalSessionTime:0.1f}s",
                  app.width/2, y, size=16, fill='white'); y += dy
        drawLabel(f"Time in good posture: {app.totalGoodTime:0.1f}s ({goodPct:0.1f}%)",
                  app.width/2, y, size=16, fill='lime'); y += dy
        drawLabel(f"Time in bad posture: {app.totalBadTime:0.1f}s ({badPct:0.1f}%)",
                  app.width/2, y, size=16, fill='red'); y += dy
        drawLabel(f"Longest good posture streak: {app.maxGoodPostureTime:0.1f}s",
                  app.width/2, y, size=16, fill='cyan'); y += dy
        drawLabel(f"Number of slouch events: {app.slouchEvents}",
                  app.width/2, y, size=16, fill='orange'); y += dy
        y += 15
        drawLabel(f"Focus Estimate: {focusLabel}",
                  app.width/2, y, size=20, fill='yellow', bold=True); y += dy
        drawLabel("We use posture stability as a proxy for focus.",
                  app.width/2, app.height - 70, size=12, fill='white')
        drawLabel("Press 'i' for focus score over time",
                  app.width/2, app.height - 45, size=12, fill='white')
    else:
        drawLabel("Focus Score Over Time", app.width/2, 50,
                  size=22, fill='white', bold=True)
        y = 100; dy = 28
        drawLabel(f"Current Focus Estimate: {focusLabel}", app.width/2, y,
                  size=18, fill='yellow', bold=True); y += dy

        if len(app.focusHistory) == 0:
            drawLabel("Not enough data yet to plot focus over time.",
                      app.width/2, y + 20, size=16, fill='white')
        else:
            topY = 130
            bottomY = app.height - 130
            leftX = 60
            rightX = app.width - 60
            drawLine(leftX, bottomY, rightX, bottomY, fill='gray', lineWidth=2)
            drawLine(leftX, topY, leftX, bottomY, fill='gray', lineWidth=2)
            drawLabel("100", leftX - 20, topY, size=12, fill='white')
            midY = (topY + bottomY) / 2
            drawLabel("50", leftX - 15, midY, size=12, fill='white')
            drawLabel("0", leftX - 10, bottomY, size=12, fill='white')
            n = len(app.focusHistory)
            duration = max(0, n - 1)
            midX = (leftX + rightX) / 2
            drawLabel("0s", leftX, bottomY + 18, size=12, fill='white', align='center')
            if duration > 1:
                drawLabel(f"{duration//2}s", midX, bottomY + 18,
                          size=12, fill='white', align='center')
            drawLabel(f"{duration}s", rightX, bottomY + 18,
                      size=12, fill='white', align='center')
            drawLabel("time (seconds since start)",
                      (leftX + rightX) / 2, bottomY + 38,
                      size=12, fill='white')

            for i, s in enumerate(app.focusHistory):
                if n == 1:
                    dotX = (leftX + rightX) / 2
                else:
                    dotX = leftX + i * (rightX - leftX) / (n - 1)
                t = s / 100
                dotY = bottomY - t * (bottomY - topY)
                drawCircle(dotX, dotY, 4, fill='yellow')

            if n >= 2:
                prevX = None; prevY = None
                for i, s in enumerate(app.focusHistory):
                    if n == 1:
                        dotX = (leftX + rightX) / 2
                    else:
                        dotX = leftX + i * (rightX - leftX) / (n - 1)
                    t = s / 100
                    dotY = bottomY - t * (bottomY - topY)
                    if prevX is not None:
                        drawLine(prevX, prevY, dotX, dotY,
                                 fill='yellow', lineWidth=1)
                    prevX, prevY = dotX, dotY
            y = bottomY + 65
            drawLabel("Each dot = your focus score at that second.",
                      app.width/2, y, size=12, fill='white'); y += 20
            drawLabel("Higher dots mean more stable, upright posture.",
                      app.width/2, y, size=12, fill='white')
        drawLabel("Press 'i' to return to summary",
                  app.width/2, app.height - 25, size=12, fill='white')

# ---------- login / menu / leaderboard drawing ----------

def drawLoginScreen(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    drawLabel("Posture Pets — Login", app.width/2, 30, size=20, fill='white', bold=True)
    drawLabel(app.loginMessage, app.width/2, 60, size=12, fill='gray')
    drawLabel("Username:", app.width/2 - 90, 120, size=16, fill='white', align='right')
    drawRect(app.width/2, 120, 220, 36, fill='white')
    uname = app.usernameInput if app.usernameInput != "" else "type here..."
    drawLabel(uname, app.width/2  + 50, 140, size=16, fill='black')
    drawLabel("Press Enter to continue", app.width/2, 170, size=12, fill='white')

def drawMenu(app):
    drawRect(0,0,app.width,app.height,fill='black')
    drawLabel(f"Welcome, {app.currentUser}", app.width/2, 40, size=20, fill="white", bold=True)
    drawLabel("1 — Start tracking", app.width/2, 110, size=16, fill="white")
    drawLabel("2 — Leaderboard", app.width/2, 150, size=16, fill="white")
    drawLabel("3 — Log out", app.width/2, 190, size=16, fill="white")
    drawLabel("When tracking: A/D switch pets, C baseline, ←/→ change mode",
              app.width/2, app.height-30, size=10, fill='gray')

def drawLeaderboard(app):
    lb = loadLeaderboard()
    drawRect(0,0,app.width,app.height,fill='black')
    drawLabel("Leaderboard (Best Good-Posture Streaks)", app.width/2, 30, size=20, fill="yellow")
    y = 70
    drawLabel("Rank", app.width/2 - 120, y, size=14, fill='white')
    drawLabel("User", app.width/2, y, size=14, fill='white')
    drawLabel("Best (s)", app.width/2 + 120, y, size=14, fill='white')
    y += 26
    for i, entry in enumerate(lb[:10]):
        drawLabel(f"{i+1}", app.width/2 - 120, y, size=16, fill='white')
        drawLabel(entry['username'], app.width/2, y, size=16, fill='white')
        drawLabel(f"{entry['score']:.1f}", app.width/2 + 120, y, size=16, fill='white')
        y += 28
    if len(lb) == 0:
        drawLabel("No scores yet.", app.width/2, app.height/2, size=16, fill='gray')
    drawLabel("Press any key to return", app.width/2, app.height - 20, size=10, fill='gray')

# ---------- redraw router ----------

def redrawAll(app):
    if app.loginState == "login":
        drawLoginScreen(app)
    elif app.loginState == "menu":
        drawMenu(app)
    elif app.loginState == "leaderboard":
        drawLeaderboard(app)
    elif app.loginState == "tracking":
        if app.mode == 'vid':
            drawVideo(app)
        elif app.mode == 'pet':
            drawPetMode(app)
        elif app.mode == 'timer':
            drawTimer(app)
        elif app.mode == 'gradient':
            drawGradient(app)
        else:
            drawSettings(app)

# ---------- skeleton drawing ----------

def drawPoseSkeleton(app, landmarks):
    connections = [
        (11, 12),  # Shoulders
        (11, 13), (13, 15),
        (12, 14), (14, 16),
        (11, 23), (12, 24),
        (23, 24),
        (23, 25), (25, 27),
        (24, 26), (26, 28),
        (0, 11), (0, 12),
    ]
    for start, end in connections:
        x1 = landmarks[start].x * app.width
        y1 = landmarks[start].y * app.height
        x2 = landmarks[end].x * app.width
        y2 = landmarks[end].y * app.height
        drawLine(x1, y1, x2, y2, fill='lime', lineWidth=3)
    keyPoints = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for i in keyPoints:
        x = landmarks[i].x * app.width
        y = landmarks[i].y * app.height
        drawCircle(x, y, 5, fill='red')

# ---------- shutdown ----------

def onAppStop(app):
    saveCurrentUserData(app)
    try:
        app.cap.release()
    except:
        pass

def main():
    runApp(width=400, height=400)

main()
