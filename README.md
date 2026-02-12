# Social Robotics Practical — Assignment 1 (WOW Game)

This repository contains our implementation of the **With Other Words (WOW)** spoken game for the **Alpha Mini** robot.

## Requirements

- **Python 3.8+**
- A working internet connection (for the robot platform + Gemini API)
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

### 2) Install dependencies
The required packges will be installed with this command.

```bash
pip install -r requirements.txt
```

### Notes

The robot realm is required to connect (found in the robot portal). Replace the realm with the correct one in `main.py`.

```python
 realm="rie.698d8be5946951d690d13ad6"
```

Insert your Gemini API key in the placeholder near the top of `main.py`.

```python
chatbot = genai.Client(api_key="api_key")
```