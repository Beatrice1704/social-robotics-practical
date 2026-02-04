# Social Robotics Practical — Assignment 1 (WOW Game)

This repository contains our implementation of the **With Other Words (WOW)** spoken game for the **Alpha Mini** robot, including:
- Robot connection via the Robots in de Klas WAMP server
- Speech output (TTS)
- Speech input (STT) using the Alpha Mini `SpeechToText` approach
- An interface to the **Gemini** LLM API

## Requirements

- **Python 3.8+**
- A working internet connection (robot platform + Gemini API)
- Access to an Alpha Mini robot realm (from `portal.robotsindeklas.nl`)
- A **Gemini API key**

## Setup

### 1) Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install robot dependencies
The required packges will be installed with this command.

```bash
pip install -r requirements.txt
```

### Notes

The robot realm is required to connect (found in the robot portal). Insert it instead of the placeholder in main.py.

```python
 realm="ENTER YOUR REALM HERE"
```

Insert your real Gemini API key in the placeholder near the top of main.py.

```python
GEMINI_API_KEY = "INSERT YOUR KEY HERE"
```