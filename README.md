# FlexAI Personal Trainer (Team B)

An AI-Powered Fitness Assistant that provides real-time posture correction, rep counting, and fatigue tracking using MediaPipe Pose Detection.

## How it works (Frontend ↔ Backend Integration)
Yes! The Web Dashboard frontend is fully connected to the AI logic backend:
1. When you select an exercise from the **Dashboard**, Flask receives the request on the `/start/<exercise>` route.
2. The server spawns a **Background Thread** to run the OpenCV Camera Loop so the web interface doesn't freeze.
3. The camera loop instantiates the specific AI Trainer class from `logic.py` (e.g., `Squat()`) and feeds it skeleton data from MediaPipe (`vision_engine.py`).
4. Upon finishing the exercise (or pressing `Q`), the backend saves the total reps, fatigue warning status, and workout duration directly into the `workouts.db` SQLite database.
5. The Web UI's History, Analytics, and Dashboard pages dynamically query this database to render charts and unlock gamification achievements.

---

## Team Setup Instructions (How to run locally)

If you are a team member pulling this repository to your laptop, follow these exact steps to run the Web Dashboard:

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd gym-trainer-personal-backup
```

### 2. Create a Virtual Environment (Recommended but optional)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Make sure you install the required packages using the newly added `requirements.txt` file:
```bash
pip install -r requirements.txt
```
*(This installs OpenCV, MediaPipe, Flask, NumPy, and pyttsx3).*

### 4. Run the Web Server
Launch the Flask application from the `team_b_application` folder:
```bash
python team_b_application/web_app.py
```

### 5. Open the Dashboard!
Once the server prints `Running on http://127.0.0.1:5000`, open your web browser and go to:
👉 **[http://localhost:5000](http://localhost:5000)**

From there, you can browse the exercises. Clicking **"Start Workout"** on an exercise page will automatically open your webcam and begin tracking your reps using the AI models!

---

### Terminal Version
If you want to run the terminal-only simulator without the web UI (for debugging logic):
```bash
python team_b_application/app.py
```
