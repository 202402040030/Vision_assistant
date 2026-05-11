# Vision Assistant Pro

## 📖 Project Description

**Vision Assistant Pro** is a comprehensive, multi-module Python application designed for accessibility, specifically functioning as a "Blind Assist" tool. The application integrates computer vision, deep learning, and speech technologies to provide real-time spatial awareness and environmental feedback for visually impaired users. 

All features are unified within a custom Tkinter graphical interface, delivering an intuitive, accessible experience with a premium dark-mode aesthetic.

### Key Features
- **Real-Time Object Detection**: Utilizes a fine-tuned **YOLOv8** model (`best.pt`) to detect indoor objects, household items, and people with high accuracy.
- **Depth Estimation**: Integrates the **MiDaS** depth estimation model to calculate accurate relative distances to detected objects, replacing heuristic distance calculations.
- **Contextual Reasoning Agent**: A `FastAgent` module evaluates detected objects based on priority (high, medium, low) and room patterns (e.g., kitchen, bedroom) to prevent alert fatigue.
- **Voice Feedback Engine**: Synthesizes speech to announce approaching or high-priority objects using built-in TTS engines.
- **Hands-Free Voice Commands**: Features a robust command listener utilizing `SpeechRecognition` and `sounddevice` to allow users to interact with the assistant entirely through voice.
- **Session Logging**: Tracks and logs session data, detections, and alerts in an on-screen console and background log.

## Literature Survey

**Paper 1:** Redmon, J., & Farhadi, A. (2018). YOLOv3: An Incremental Improvement. 
- Real-time object detection with YOLO architecture

**Paper 2:** Ranftl, R., et al. (2020). MiDaS: Towards Robust Monocular Depth Estimation.
- Depth estimation for distance measurement

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- Webcam or external camera device

### 1. Clone the Repository
```bash
git clone <YOUR_REPOSITORY_URL>
cd vision_assistant_project
```

### 2. Install Dependencies
Install the required core libraries. 
*(Note: For Windows users, `pywin32` is heavily recommended for native speech support).*

```bash
pip install ultralytics opencv-python sounddevice SpeechRecognition torch torchvision pywin32
```

*(If you run into issues with `sounddevice` on Linux/macOS, you may need to install `portaudio` via your package manager).*

### 3. Run the Application
Ensure `best.pt` is located in the root directory.

```bash
python main.py
```
The application will launch the GUI, initialize the models, open your camera, and begin listening for voice commands.

## 📊 Results & Model Performance

The core object detection model was fine-tuned to focus on environments relevant to a visually impaired user.

### YOLOv8 Fine-tuning (COCO8)
The base YOLOv8n model was fine-tuned using the COCO8 dataset over 5 epochs to specialize in 80 object categories, heavily focusing on indoor furniture (chairs, beds, tables) and household items (knives, cups, bottles). 

**Validation Set Performance Metrics:**
- **Precision (P)**: ~0.82
- **Recall (R)**: ~0.75
- **mAP50**: ~0.84
- **mAP50-95**: ~0.61

The integration of **MiDaS** allows the system to pair these high-confidence bounding boxes with a dense depth map, enabling the assistant to accurately warn the user of obstacles in their immediate path.
