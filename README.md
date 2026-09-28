# Auto-Bot-Game-using-OCR

A Python-based intelligent GUI automation framework that combines **computer vision, OCR, Windows GUI automation, and state-based decision making** to automate repetitive tasks in graphical applications.

The project is designed with a modular architecture so that visual recognition, OCR, automation, and decision-making components can be developed and improved independently.

## Overview

Traditional GUI automation often relies on fixed screen coordinates:

```text
Move to (x, y)
       ↓
     Click
       ↓
     Wait
       ↓
Move to (x, y)
```

This approach is fragile because the interface may change depending on the window position, resolution, UI state, or application content.

This project aims to build a more robust approach:

```text
                 Application Window
                        │
                        ▼
                  Window Capture
                        │
                        ▼
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       Computer Vision           OCR
       / Template Matching       Text Recognition
              │                   │
              └─────────┬─────────┘
                        ▼
                 Perception Layer
                        │
                        ▼
                  State Machine
                        │
                        ▼
                 Decision Layer
                        │
                        ▼
                 Action Controller
                        │
                        ▼
                  GUI Automation
```

The goal is to allow the automation system to **observe the application, understand its current state, make a decision, and perform an appropriate action**.

---

## Key Features

### Computer Vision

The project uses OpenCV for visual analysis and UI element detection.

Current capabilities include:

* Image capture
* Region-of-interest extraction
* Template matching
* Confidence-based detection
* Visual template management
* UI state detection

Example:

```text
Screenshot
    │
    ▼
OpenCV Processing
    │
    ▼
Template Matching
    │
    ▼
Detected UI Element
    │
    ▼
Confidence Score
```

---

### OCR

OCR is designed to provide text-based perception in addition to visual template recognition.

The project includes `pytesseract` as the OCR interface.

OCR can be used to extract information such as:

* Button labels
* Mission names
* Status messages
* Counters
* Notifications
* Other dynamic text

Example:

```text
Image
  │
  ▼
OCR
  │
  ▼
"Start Mission"
  │
  ▼
Decision System
  │
  ▼
Click Start Mission
```

OCR is complementary to template matching:

```text
Template Matching
    → "Where is the button?"

OCR
    → "What does the button say?"
```

---

## Background GUI Automation

The project provides Windows-specific automation capabilities for interacting with an application window.

Instead of relying exclusively on physical mouse movement, the system can send input directly to the target window using Windows APIs.

Supported operations include:

* Background mouse clicks
* Mouse movement
* Keyboard input
* Client-coordinate handling
* Window-specific interaction

This allows the automation system to operate independently from the user's normal desktop interaction.

---

## State Machine

The automation logic is designed around a state machine rather than a simple sequence of hard-coded actions.

A typical workflow is:

```text
START
  │
  ▼
OBSERVE
  │
  ▼
RECOGNIZE
  │
  ▼
DETERMINE STATE
  │
  ▼
MAKE DECISION
  │
  ▼
EXECUTE ACTION
  │
  ▼
WAIT FOR RESULT
  │
  └──────────────► OBSERVE
```

This architecture makes the automation system easier to extend and recover from unexpected UI states.

---

## Modular Architecture

The project separates perception, decision-making, and action execution.

```text
Auto-Bot-Game-using-OCR
│
├── assets/
│   └── templates/
│       ├── missions/
│       └── active_quests/
│
├── bot/
│   ├── controller.py
│   ├── state_machine.py
│   ├── bot.py
│   └── window_controller.py
│
├── config/
│   ├── missions.yaml
│   └── active_quests.yaml
│
├── tools/
│   ├── capture_missions.py
│   ├── capture_mission_templates.py
│   ├── capture_active_quests.py
│   └── capture_active_quest_templates.py
│
├── vision/
│   ├── capture.py
│   ├── detector.py
│   ├── template.py
│   └── window_capture.py
│
├── config.yaml
├── main.py
└── requirements.txt
```

### `vision/`

Responsible for perception and image processing.

* Screen capture
* Window capture
* Image processing
* Template matching
* Visual detection
* OCR integration

### `bot/`

Responsible for automation and decision-making.

* State management
* Action control
* Window-specific input
* Main bot orchestration

### `tools/`

Development utilities for:

* Collecting visual samples
* Creating templates
* Calibrating regions
* Preparing recognition data

### `config/`

Contains external configuration and calibration data.

This keeps application-specific parameters separate from the core Python code.

---

## Perception Architecture

The perception layer is designed to support multiple recognition techniques.

```text
                    Input Image
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
       Template Matching            OCR
             │                       │
             ▼                       ▼
       Visual Features          Text Features
             │                       │
             └───────────┬───────────┘
                         ▼
                  Perception Model
                         │
                         ▼
                  Structured State
```

A future implementation can also incorporate machine-learning or deep-learning models when traditional template matching or OCR is insufficient.

---

## AI Integration

The architecture is designed to be **AI-ready**.

Potential AI components include:

* Deep-learning object detection
* Neural OCR
* Vision-language models
* Image classification
* Semantic text classification
* Intelligent action selection

For example:

```text
Application
    │
    ▼
Screenshot
    │
    ├── OpenCV
    │
    ├── OCR
    │
    └── AI Vision Model
             │
             ▼
        Unified Perception
             │
             ▼
        Decision Engine
             │
             ▼
        GUI Controller
```

The current system does not require a large AI model for basic visual detection. AI components can be introduced selectively where they provide additional robustness.

---

## Template Dataset

Visual templates are organized by semantic category.

Example:

```text
assets/templates/
│
├── missions/
│   ├── category_a/
│   │   ├── 001.png
│   │   └── 002.png
│   │
│   └── category_b/
│       └── 001.png
│
└── active_quests/
    ├── category_a/
    │   └── 001.png
    │
    └── unknown.png
```

Multiple samples can be collected for the same visual category.

This makes it possible to improve recognition robustness without modifying the core detection system.

---

## Installation

### Requirements

* Windows
* Python 3.x
* Git

### Clone the Repository

```bash
git clone https://github.com/DOPHANK/Auto-Bot-Game-using-OCR.git
cd Auto-Bot-Game-using-OCR
```

### Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## Running the Application

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the application:

```powershell
python main.py
```

Development tools can also be executed independently.

For example:

```powershell
python -m tools.capture_missions
```

---

## Development Workflow

The project follows an iterative development process:

```text
1. Capture application UI
          │
          ▼
2. Collect visual samples
          │
          ▼
3. Build templates
          │
          ▼
4. Implement recognition
          │
          ▼
5. Integrate OCR
          │
          ▼
6. Build state machine
          │
          ▼
7. Implement automated actions
          │
          ▼
8. Test and improve
```

Git is used to maintain development checkpoints.

Example:

```bash
git add .
git commit -m "Add OCR detector"
git push
```

---

## Technology Stack

| Technology    | Purpose                                |
| ------------- | -------------------------------------- |
| Python        | Core application                       |
| OpenCV        | Computer vision                        |
| NumPy         | Image processing                       |
| MSS           | Screen capture                         |
| PyWin32       | Windows API and background interaction |
| PyAutoGUI     | GUI automation                         |
| PyYAML        | Configuration                          |
| Tesseract OCR | Text recognition                       |
| Git           | Version control                        |
| GitHub        | Source code management                 |

---

## Roadmap

### Perception

* [x] Window capture
* [x] Screen capture
* [x] Template matching
* [x] Visual template collection
* [ ] OCR detector integration
* [ ] OCR confidence handling
* [ ] Multi-method perception fusion
* [ ] AI-based visual recognition

### Automation

* [x] Background mouse interaction
* [x] Background keyboard interaction
* [x] Window-specific controller
* [x] State machine foundation
* [ ] Automated decision engine
* [ ] Automatic task selection
* [ ] Automatic task completion detection
* [ ] Error recovery

### Intelligence

* [ ] Semantic text classification
* [ ] Vision-language model integration
* [ ] Dynamic UI understanding
* [ ] Adaptive action selection
* [ ] Self-improving recognition pipeline

---

## Project Status

This project is currently under active development.

The current implementation provides the foundation for a vision-driven GUI automation system, including:

* Windows-specific window capture
* Background GUI interaction
* OpenCV-based visual recognition
* Template collection
* Configuration-driven regions
* State-machine architecture
* OCR-ready infrastructure

The next stage focuses on integrating OCR into the perception pipeline and combining visual and textual information to improve automated decision-making.

---

## Disclaimer

This project is intended for educational, research, and personal automation purposes.

Automated interaction with third-party applications may be restricted by their terms of service. Users are responsible for ensuring that their use of the software complies with applicable rules and policies.
