---
title: AISL Sign Language App
emoji: 🤟
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.40.1
app_file: app.py
pinned: false
---

# AISL - AI Sign Language Learning App

AISL is a Streamlit-based application designed to assist users in learning sign language (ASL/ISL) using real-time computer vision. The app leverages Python and machine learning to track hand movements and provide feedback.

## 🚀 Features

* **Real-time Hand Tracking:** Uses MediaPipe to detect hand landmarks from your webcam.
* **Interactive Learning:** * **User-Friendly Interface:** Built with Streamlit for an easy-to-use web experience.

## 🛠️ Tech Stack

* **Python 3.x**
* **Streamlit** - For the web interface.
* **MediaPipe** - For hand tracking and gesture recognition.
* **OpenCV** - For image processing.
* **NumPy**

## 📦 Installation

To run this app locally:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/anat-T/AISL.git](https://github.com/anat-T/AISL.git)
    cd AISL
    ```

2.  **Create and activate the environment:**
    ```bash
    conda create -n aisl-env python=3.9
    conda activate aisl-env
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```
    *(Note: Replace `app.py` with your main filename if it differs).*

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)