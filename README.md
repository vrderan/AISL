# 🤟 AISL - Interactive Sign Language Learning App

An interactive, AI-powered application for learning Sign Language (ASL & ISL) in real-time. The app uses computer vision to track your hands and provides instant feedback on your signing accuracy.

## ✨ Features
* **Real-time AI Feedback:** Uses MediaPipe and Machine/Deep-learning models to detect hand landmarks and evaluate your signing.
* **Gamified Learning:** Progress bars, success animations, and mastery levels for every sign.
* **Multi-Language Support:** Includes support for both American Sign Language (ASL) and Israeli Sign Language (ISL).
* **Interactive Video Instructions:** Built-in video examples and guides for every sign.

## 🛠️ Prerequisites
* **Python 3.10** (Strictly Required for MediaPipe compatibility).
* **Git Large File Storage (LFS)** (Required for downloading models/images).
* A computer with a **decent CPU** for running the app locally.
* **Webcam**.
* **Well lit environment** to allow proper hand tracking.

## 📝 Note
There is a deployed version of this app, however it did not run smoothly enough to be usable due to its live video stream and processing demands. Please run the app locally by following the instructions below.

## 🚀 Installation Guide

### 0. Install Git LFS (Important!)
This repository contains large model files and images. You must install Git LFS **before** cloning to ensure these files are downloaded correctly.

**Windows / Mac / Linux:**
```bash
git lfs install
```
(If the command is not found, download and install it from git-lfs.com)

### 1. Clone the Repository
```bash
git clone [https://github.com/vrderan/AISL.git](https://github.com/vrderan/AISL.git)
cd AISL
```

### 2. Set Up Virtual Environment
You must use **Python 3.10**. Newer versions (3.11+) may cause conflicts with the computer vision libraries.

**Option A: Using Conda (Recommended)**
This is the easiest way to ensure you have the correct Python version.

```bash
# 1. Create a new environment with Python 3.10
conda create -n aisl_app python=3.10

# 2. Activate the environment
conda activate aisl_app
```

**Option B: Using Standard Python (venv)**
Commands may vary depending on your OS installation. First, check which command runs Python 3.10 on your machine:

```bash
python --version   # OR
python3 --version  # OR
py --list          # (Windows)
```

Use the command that returns Python 3.10.x to create the environment:

Windows:
```bash
py -3.10 -m venv venv
.\venv\Scripts\activate
```

Mac / Linux:
```bash
# Use 'python3' or 'python' depending on your setup
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Once your environment is active (and showing aisl_app or venv in the terminal), install the required packages:

```bash
pip install -r requirements.txt
```
Note: On Mac/Linux, if pip doesn't work, try using pip3.

### ▶️ How to Run
Launch the application using Streamlit:

```bash
streamlit run app.py
```

### 📂 Project Structure
* app.py: The main entry point.
* views/: Contains the UI logic for Learning and Practice pages.
* utils/: Helper functions for video processing, state management, and data. Also contains the trained models.
* images/: Contains fingerspelling instructions and app logo.

### ⚠️ Troubleshooting
**"AttributeError: module 'mediapipe' has no attribute 'solutions'"** This usually happens if a newer version of protobuf was installed automatically. Fix: Run this command to force the compatible versions:

```bash
pip install mediapipe==0.10.14 protobuf==4.25.3 streamlit-extras==0.6.0
```

**"Feedback manager requires a model with a single signature..."** This is a harmless warning from the underlying MediaPipe engine. You can safely ignore it; the app will function correctly.

**Images are broken or "UnidentifiedImageError"** This usually means Git LFS wasn't installed before cloning, so you downloaded "pointer files" instead of real images.