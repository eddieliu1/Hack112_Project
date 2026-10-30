Project Title: [Posture Protector]

In this file, please specify:
- Which award categories you are submitting for
- What external modules you used (if any) and how to install them
- How to run your program
- A General description of your program
- Basic controls for your program

Award Categories
We are submitting Posture Protector Social Good Category and Best Overall Category

External Modules & Installation
Required Libraries
1. OpenCV (opencv-python)
Purpose: Captures video feed from your webcam and processes video frames
Used in: main.py - video capture and frame processing
Installation:
bash
     pip install opencv-python
2. MediaPipe (mediapipe)
Purpose: Real-time human pose estimation - detects body landmarks (nose, shoulders, elbows, etc.)
Used in: main.py - posture analysis, landmark detection, skeleton extraction
Why it's used: MediaPipe's lightweight pose model runs efficiently on CPU, tracking 33 body landmarks including key posture indicators (shoulders, neck position, spine alignment)
Installation:
bash
     pip install mediapipe
3. Pillow (Pillow)
Purpose: Image processing and format conversion
Used in: Converting OpenCV frames (BGR format) to RGB for display
Installation:
bash
     pip install Pillow
4. CMU Graphics (cmu-graphics)
5. json
6. os

How to Run Your Program

Step 1: Run the Main Application (main.py)
Enter your username
Access three main features: Start Tracking, Leaderboard, Log Out
Step 2: Start Tracking
After clicking "Start Tracking", you'll see a small window (160×130 by default) displaying mode options. Use arrow keys (← / →) to navigate between modes.

General Description
Posture Guardian is an intelligent posture tracking application designed for students, developers, and anyone working extended hours at a computer. The application uses your webcam and advanced pose estimation to:

Monitor your posture in real-time with multiple visualization modes (live feed, gradient color feedback, and timer)
Gamify posture improvement through a customizable pet companion that grows, evolves, and gains XP as you maintain good posture
Track long-term focus and wellness with analytics dashboards showing slouch events, focus scores over time, and personal records
Maintain persistent user profiles with login authentication so your progress syncs across sessions
Compete with others via a leaderboard system that ranks users by their focus scores and streaks
The application targets:

Basic Controls
Main Application (After Login)
Mode Navigation:

Right Arrow (→) - Cycle to next mode
Left Arrow (←) - Cycle to previous mode
Available Modes:
1. Video Mode
What it shows: Live webcam feed with pose skeleton overlay (limbs drawn as lines)
Purpose: See yourself and your posture in real-time
Special Control:
Press 'C' to capture your baseline posture (good posture reference point)
2. Pet Mode
What it shows: Your customizable pet companion with XP bar and level
Purpose: Gamified motivation - pet bounces when you have good posture, evolves at each level
How it works: Pet mood updates based on posture; gains XP during good posture, loses XP during slouching
Unlocks: New pets at levels 1, 2, 3, 4, 5 (blob → duck → axolotl → scotty → dragon)
3. Timer Mode
What it shows: Large current streak timer (green for good posture, red for bad posture)
Purpose: Instant feedback on how long you've maintained (or failed to maintain) good posture
Display:
Green timer = current good posture streak
Red timer = current slouch duration
Max time shown in bottom-right corner (your personal record)
Window behavior: Window grows if you slouch for >7 seconds (visual penalty)
4. Gradient Mode
What it shows: Full-screen color gradient from green → yellow → red
Purpose: Subtle visual feedback on posture quality in real-time
Color mapping:
Green = perfect upright posture
Yellow = mild slouch
Red = severe forward head posture
5. Settings/Analytics Mode 
What it shows: Comprehensive focus report with stats and optional dot-plot graph
Purpose: Long-term analytics and wellness insights
Displays:
Total session time, time in good/bad posture, percentages
Longest good posture streak (personal record)
Number of slouch events (transitions from good → bad)
Focus Estimate (HIGH / MEDIUM / LOW) based on weighted scoring
Special Control: Press 'i' to toggle between summary view and focus score graph
Summary View: Overview of all metrics
Dot Plot View: Visual graph showing focus score over time (one sample per second)
Global Controls:

'C' (in Video mode) - Capture baseline posture,   
'i' (in Settings mode) - Toggle between summary and detailed graph view,   
'Q' - Quit application


Thank you for using Posture Guardian! Maintain good posture, earn XP, and level up your wellness. 



Video Demo: https://drive.google.com/file/d/1O2uh5PItSZXJRqG5Ov9upUu_Wss26M4I/view?usp=sharing
# Hack112_Project
