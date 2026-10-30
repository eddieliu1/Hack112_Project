# Posture Protector

Posture Protector is a desktop app that uses your webcam to watch your posture while you work. It detects when your head drops toward your shoulders and gives you live feedback through a timer, a color display, and a virtual pet that grows when you sit up straight.

Built for Hack112 by group 34. We are submitting to the **Social Good** and **Best Overall** categories.

**[Watch the video demo](https://drive.google.com/file/d/1O2uh5PItSZXJRqG5Ov9upUu_Wss26M4I/view?usp=sharing)**

## Features

- **Real-time posture tracking** using pose detection on your webcam feed
- **Five display modes**, from a full video view to a small timer you can leave in the corner of your screen
- **A virtual pet** that earns XP and unlocks new pets as you hold good posture
- **A focus report** with your posture stats and a graph of your focus score over time
- **User profiles and a leaderboard** ranked by each user's longest good-posture streak

## Requirements

- Python 3.11 (`mediapipe==0.10.21` is not available for Python 3.13)
- A webcam
- An internet connection, because the pet images load from the web

The app has been tested on macOS with Apple Silicon. On macOS, allow camera access for your terminal or editor under **System Settings > Privacy & Security > Camera**.

## Setup

Clone the repository, then run these commands from the project root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install "mediapipe==0.10.21" Pillow
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

The `mediapipe` version must stay pinned: newer releases removed the `mp.solutions` API this app uses. Installing it also installs OpenCV. CMU Graphics is included in `src/cmu_graphics`, so it doesn't need to be installed.

## Running the app

Run this from the project root, so your profile and leaderboard data load from the right place:

```bash
python src/main.py
```

1. Type a username (letters and numbers only) and press **Enter**. There is no password, and a new username creates a new profile.
2. Press **1** to start tracking.
3. Sit up straight in view of the camera and press **C** to capture your baseline posture. Until you do this, slouch detection uses a generic default and Gradient mode stays green.
4. Use the **left and right arrow keys** to switch between display modes.
5. Press **Q** to save your progress and stop the camera, then close the window. Closing the window directly also saves your progress.

## Controls

| Screen | Key | Action |
| --- | --- | --- |
| Login | Letters and numbers, **Backspace**, **Enter** | Type your username and log in |
| Menu | **1** | Start tracking |
| Menu | **2** | View the leaderboard (press any key to return) |
| Menu | **3** | Log out |
| Tracking | **Left / Right arrows** | Switch display mode |
| Tracking | **C** | Capture baseline posture |
| Tracking | **Q** | Save and stop the camera |
| Pet mode | **A / D** | Switch between unlocked pets |
| Pet mode | **U** | Add 25 XP (for testing and demos) |
| Settings mode | **I** | Switch between the summary and the focus graph |

## Display modes

| Mode | What it shows |
| --- | --- |
| **Video** | Your webcam feed with a pose skeleton drawn on top |
| **Pet** | Your pet, its level, and its XP bar. The pet looks happy during good posture and sad when you slouch. |
| **Timer** | Your current streak in green, or your current slouch time in red, plus your best streak. If you slouch for more than 7 seconds, the window starts to grow. |
| **Gradient** | A solid color that shifts from green to red as your head drops below your baseline |
| **Settings** | Your session time, time in good and bad posture, best streak, slouch count, and focus estimate. Press **I** for the focus score graph. |

## How it works

**Posture detection:** MediaPipe Pose finds your nose and shoulders in each webcam frame. The app compares the vertical distance between them to your baseline, and counts you as slouching if your nose gets too close to shoulder height. If you aren't visible to the camera, that also counts as bad posture.

**Pet progression:** Your pet earns about 1 XP per second of good posture, and slouching pauses XP without removing any. Level 1 needs 20 XP, and each level after that needs 1.5 times as much. New pets unlock at each level up to level 5: blob, duck, axolotl, scotty, and dragon. Pet progress resets each time you start the app.

**Focus score:** The score runs from 0 to 100 and appears after 10 seconds of tracking. A score of 70 or above is HIGH, 40 or above is MEDIUM, and anything lower is LOW. It uses posture stability as a stand-in for focus, weighted as follows:

- 50%: percentage of time in good posture
- 30%: longest good-posture streak, capped at 60 seconds
- 20%: stability, which drops to zero at 10 slouch events

## Project structure

| Path | Purpose |
| --- | --- |
| `src/main.py` | The main application |
| `src/cmu_graphics/` | Bundled CMU Graphics library |
| `users/` | Saved stats for each user |
| `leaderboard.json` | Saved leaderboard scores |
| `max_posture_time.txt` | Best streak used before a user logs in |
| `pet.py` | Standalone prototype of the pet feature, not used by the main app |

All data is stored locally on your computer, and video isn't saved. The leaderboard only includes users on the same copy of the project.

## Built with

- [OpenCV](https://opencv.org/) for webcam capture and frame processing
- [MediaPipe](https://developers.google.com/mediapipe) for pose detection
- [Pillow](https://python-pillow.org/) for image conversion
- [CMU Graphics](https://academy.cs.cmu.edu/desktop) for the app window and drawing
