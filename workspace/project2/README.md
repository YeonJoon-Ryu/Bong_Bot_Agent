# Project2

## Description
This project captures video from the webcam and uses **OpenCV** together with **MediaPipe** to draw a real‑time skeleton of the human body (pose) and hand landmarks. It demonstrates how to combine `mp.solutions.pose` and `mp.solutions.hands` for simultaneous pose and hand tracking.

## Requirements
- Python 3.x
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe==0.10.35`)
- protobuf `<4`

The required packages are listed in `requirements.txt`.

## Setup
```bat
# Create virtual environment (already done)
python -m venv .venv

# Activate the virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1   # or .\.venv\Scripts\activate.bat for cmd

# Install dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run
```bat
.\.venv\Scripts\python.exe main.py
```

Press **ESC** to close the window.
