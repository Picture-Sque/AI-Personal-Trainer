"""
Flask Web Application for AI Personal Trainer.
Premium dark-themed dashboard with workout history, analytics, and exercise management.
"""
import subprocess
import sys
import json
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify
import database as db

app = Flask(__name__)

# ==========================================
# EXERCISE DATA (metadata for UI)
# ==========================================
EXERCISES = {
    'squat': {
        'id': 'squat',
        'name': 'Squat',
        'class_name': 'Squat',
        'muscle_group': 'Legs & Glutes',
        'difficulty': 'Beginner',
        'camera_view': 'Side',
        'image': 'squat.png',
        'color': '#7c3aed',
        'description': 'A compound lower body exercise that targets your quadriceps, hamstrings, and glutes.',
        'instructions': [
            'Stand with your left side facing the camera',
            'Place feet shoulder-width apart',
            'Keep your chest up and back straight',
            'Bend your knees and lower your hips as if sitting in a chair',
            'Go down until thighs are parallel to the floor (knee angle ~90°)',
            'Push through your heels to stand back up'
        ],
        'avoid': [
            'Letting your knees cave inward',
            'Leaning too far forward',
            'Not going deep enough',
            'Lifting heels off the ground'
        ],
        'tracking_info': 'We track your knee angle and back angle from the side view to ensure proper squat depth and posture.',
        'target_angle': 'Knee angle: aim for 90° at the bottom',
        'demo_video': 'YaXPRqUwItQ'
    },
    'bicep_curl': {
        'id': 'bicep_curl',
        'name': 'Bicep Curl',
        'class_name': 'BicepCurl',
        'muscle_group': 'Biceps',
        'difficulty': 'Beginner',
        'camera_view': 'Side',
        'image': 'bicep_curl.png',
        'color': '#06b6d4',
        'description': 'An isolation exercise that targets your biceps. Stand sideways to the camera and curl with the arm closest to it.',
        'instructions': [
            'Stand with your left side facing the camera',
            'Hold the weight in your left hand, arm fully extended',
            'Keep your elbow pinned to your side throughout',
            'Curl the weight up by bending at the elbow',
            'Squeeze at the top when your hand is near your shoulder',
            'Slowly lower back down with control'
        ],
        'avoid': [
            'Swinging your elbow forward (using your shoulder)',
            'Not curling all the way up (half reps)',
            'Using momentum instead of controlled muscle contraction',
            'Moving your upper arm during the curl'
        ],
        'tracking_info': 'We track your elbow angle from the side view and monitor shoulder movement to detect swinging or using momentum.',
        'target_angle': 'Elbow angle: aim for <40° at the top of the curl',
        'demo_video': 'ykJmrZ5v0Oo'
    },
    'jumping_jacks': {
        'id': 'jumping_jacks',
        'name': 'Jumping Jacks',
        'class_name': 'JumpingJacks',
        'muscle_group': 'Full Body Cardio',
        'difficulty': 'Beginner',
        'camera_view': 'Front',
        'image': 'jumping_jacks.png',
        'color': '#10b981',
        'description': 'A full-body cardio exercise that raises your heart rate while working your entire body.',
        'instructions': [
            'Start standing with arms at your sides and feet together',
            'Jump out: spread your legs wide and raise arms overhead simultaneously',
            'Jump in: bring feet back together and arms to your sides',
            'Maintain a steady, rhythmic pace',
            'Keep your knees straight throughout the movement'
        ],
        'avoid': [
            'Bending your knees too much',
            'Jumping asymmetrically (one leg only)',
            'Not raising arms fully overhead',
            'Leaning to one side'
        ],
        'tracking_info': 'We track both arm angles, leg symmetry, knee straightness, and body center balance.',
        'target_angle': 'Arms: above 140° when spread, below 60° when closed',
        'demo_video': 'CWpmIW6l-YA'
    },
    'shoulder_press': {
        'id': 'shoulder_press',
        'name': 'Shoulder Press',
        'class_name': 'ShoulderPress',
        'muscle_group': 'Shoulders & Triceps',
        'difficulty': 'Intermediate',
        'camera_view': 'Front',
        'image': 'shoulder_press.png',
        'color': '#f59e0b',
        'description': 'An overhead pressing movement that builds shoulder strength and stability.',
        'instructions': [
            'Stand with feet shoulder-width apart',
            'Start with elbows bent at 90° at shoulder height',
            'Press both arms straight overhead simultaneously',
            'Fully extend your arms at the top',
            'Lower back to the starting position with control'
        ],
        'avoid': [
            'Leaning back (arching your spine)',
            'Pressing unevenly (one arm higher)',
            'Not fully extending at the top',
            'Using momentum to push the weight up'
        ],
        'tracking_info': 'We track both elbow angles for symmetry and your back angle to prevent dangerous leaning.',
        'target_angle': 'Elbow angle: >160° at top, <90° at bottom',
        'demo_video': 'qEwKCR5JCog'
    },
    'lunge': {
        'id': 'lunge',
        'name': 'Lunge',
        'class_name': 'Lunge',
        'muscle_group': 'Legs & Glutes',
        'difficulty': 'Intermediate',
        'camera_view': 'Side',
        'image': 'lunge.png',
        'color': '#ec4899',
        'description': 'A unilateral leg exercise that improves balance, coordination, and leg strength.',
        'instructions': [
            'Stand tall with feet hip-width apart',
            'Step forward with one leg',
            'Lower your hips until front knee is at ~90°',
            'Keep your torso upright throughout',
            'Push through your front heel to stand back up'
        ],
        'avoid': [
            'Letting your front knee go past your toes',
            'Leaning your torso too far forward',
            'Doing shallow lunges (not deep enough)',
            'Losing balance by not engaging your core'
        ],
        'tracking_info': 'We track your knee angle, torso lean, and detect if your knee goes past your toes.',
        'target_angle': 'Front knee: aim for 90° at the bottom',
        'demo_video': 'QOVaHwm-Q6U'
    },
    'push_up': {
        'id': 'push_up',
        'name': 'Push-Up',
        'class_name': 'PushUp',
        'muscle_group': 'Chest, Shoulders & Triceps',
        'difficulty': 'Intermediate',
        'camera_view': 'Side',
        'image': 'push_up.png',
        'color': '#ef4444',
        'description': 'The king of bodyweight exercises. Builds pushing strength across your entire upper body.',
        'instructions': [
            'Start in a plank position with arms straight',
            'Keep your body in a straight line from head to heels',
            'Lower yourself by bending your elbows',
            'Go down until your chest nearly touches the floor',
            'Push back up to full arm extension'
        ],
        'avoid': [
            'Letting your hips sag toward the floor',
            'Piking your hips up (butt in the air)',
            'Doing half reps (not going low enough)',
            'Flaring elbows out to the sides'
        ],
        'tracking_info': 'We track your elbow angle and body line (shoulder-hip-ankle) to detect sagging or piking.',
        'target_angle': 'Elbow angle: <90° at the bottom, body line: ~180° (straight)',
        'demo_video': 'IODxDxX7oi4'
    },
    'high_knees': {
        'id': 'high_knees',
        'name': 'High Knees',
        'class_name': 'HighKnees',
        'muscle_group': 'Core & Cardio',
        'difficulty': 'Intermediate',
        'camera_view': 'Front',
        'image': 'high_knees.png',
        'color': '#14b8a6',
        'description': 'An explosive cardio exercise that strengthens your hip flexors and core while elevating heart rate.',
        'instructions': [
            'Stand tall with feet hip-width apart',
            'Drive one knee up to hip level',
            'Alternate legs rapidly: left, right, left, right',
            'Keep your torso upright (don\'t lean back)',
            'Pump your arms in rhythm with your legs'
        ],
        'avoid': [
            'Not raising knees high enough (below hip level)',
            'Leaning backward to fake knee height',
            'Only lifting one leg repeatedly',
            'Going too slowly (maintain cardio pace)'
        ],
        'tracking_info': 'We track both hip angles, leg alternation, and torso lean. Every 2 knee raises = 1 rep.',
        'target_angle': 'Hip angle: <70° when knee is raised',
        'demo_video': 'D0VjPEz7Z_4'
    },
    'lateral_raise': {
        'id': 'lateral_raise',
        'name': 'Lateral Raise',
        'class_name': 'LateralRaise',
        'muscle_group': 'Shoulders (Deltoids)',
        'difficulty': 'Beginner',
        'camera_view': 'Front',
        'image': 'lateral_raise.png',
        'color': '#8b5cf6',
        'description': 'An isolation exercise that sculpts and strengthens the side deltoid muscles for broader shoulders.',
        'instructions': [
            'Stand with arms at your sides',
            'Keep your arms straight (slight elbow bend only)',
            'Raise both arms out to the sides until shoulder height',
            'Pause briefly at the top',
            'Lower back down with control'
        ],
        'avoid': [
            'Bending your elbows too much',
            'Shrugging your shoulders up',
            'Raising arms above shoulder level',
            'Swinging or using momentum'
        ],
        'tracking_info': 'We track both shoulder angles, elbow straightness, shoulder shrugging, and arm symmetry.',
        'target_angle': 'Shoulder angle: ~80-90° at the top (shoulder height)',
        'demo_video': 'XPPfnSEATJA'
    }
}


# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def dashboard():
    stats = db.get_dashboard_stats()
    recent = db.get_recent_workouts(5)
    achievements = db.get_achievements()
    return render_template('dashboard.html',
                           stats=stats,
                           recent=recent,
                           achievements=achievements,
                           exercises=EXERCISES)


@app.route('/exercises')
def exercises():
    return render_template('exercises.html', exercises=EXERCISES)


@app.route('/exercise/<exercise_id>')
def exercise_demo(exercise_id):
    exercise = EXERCISES.get(exercise_id)
    if not exercise:
        return redirect(url_for('exercises'))
    return render_template('exercise_demo.html', exercise=exercise)


@app.route('/start/<exercise_id>')
def start_exercise(exercise_id):
    """Launch the OpenCV camera session in a background thread."""
    exercise = EXERCISES.get(exercise_id)
    if not exercise:
        return redirect(url_for('exercises'))

    # Launch the camera session via main.py subprocess
    def run_session():
        import time as _time
        from logic import (Squat, BicepCurl, JumpingJacks, ShoulderPress,
                           Lunge, PushUp, HighKnees, LateralRaise)
        from vision_engine import VisionEngine
        from feedback import speak
        import cv2

        class_map = {
            'Squat': Squat, 'BicepCurl': BicepCurl, 'JumpingJacks': JumpingJacks,
            'ShoulderPress': ShoulderPress, 'Lunge': Lunge, 'PushUp': PushUp,
            'HighKnees': HighKnees, 'LateralRaise': LateralRaise
        }

        trainer_class = class_map.get(exercise['class_name'])
        if not trainer_class:
            return

        trainer = trainer_class()
        vision = VisionEngine()

        speak(f"Starting {trainer.name} session")

        cap = cv2.VideoCapture(0)
        session_start = _time.time()
        form_warnings = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image, landmarks = vision.process_frame(frame)

            feedback_text = ""
            if landmarks:
                rep_complete, feedback_text, angle = trainer.process(landmarks)

                # UI Drawing
                cv2.rectangle(image, (0, 0), (350, 120), (245, 117, 16), -1)
                cv2.putText(image, trainer.name.upper(), (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(trainer.reps), (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, "REPS", (20, 115),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, trainer.stage, (150, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Angle: {int(angle)}", (15, 145),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

                if feedback_text:
                    cv2.rectangle(image, (0, 420), (640, 480), (0, 0, 0), -1)
                    text_color = (0, 255, 0)
                    if any(kw in feedback_text.lower() for kw in ['menu', 'straighten', 'swing', 'lean', 'sag', 'pike',
                                                                    'bend', 'shrug', 'cave', 'uneven', 'half', 'shallow',
                                                                    'knee', 'higher', 'alternate']):
                        text_color = (0, 0, 255)
                        form_warnings += 1

                    cv2.putText(image, feedback_text, (10, 460),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2, cv2.LINE_AA)
                    speak(feedback_text)

                if trainer.game_over:
                    cv2.putText(image, "SESSION OVER", (130, 250),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5, cv2.LINE_AA)
                    cv2.imshow('AI Trainer', image)
                    cv2.waitKey(4000)
                    break

            cv2.imshow('AI Trainer', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Save workout to database
        duration = _time.time() - session_start
        avg_speed = duration / max(trainer.reps, 1)
        fatigue = 2 if trainer.game_over else 0
        if trainer.reps > 0:
            db.save_workout(
                exercise=trainer.name,
                reps=trainer.reps,
                duration=round(duration, 1),
                avg_rep_speed=round(avg_speed, 2),
                fatigue_level=fatigue,
                form_warnings=form_warnings
            )

    # Run in a thread so Flask stays responsive
    t = threading.Thread(target=run_session, daemon=True)
    t.start()

    return render_template('session_result.html', exercise=exercise)


@app.route('/history')
def history():
    workouts = db.get_all_workouts()
    return render_template('history.html', workouts=workouts)


@app.route('/analytics')
def analytics():
    data = db.get_analytics_data()
    stats = db.get_dashboard_stats()
    return render_template('analytics.html', data=data, stats=stats)


# ==========================================
# API ENDPOINTS (for AJAX)
# ==========================================

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_dashboard_stats())


@app.route('/api/recent')
def api_recent():
    return jsonify(db.get_recent_workouts(5))


@app.route('/api/analytics')
def api_analytics():
    return jsonify(db.get_analytics_data())


@app.route('/api/achievements')
def api_achievements():
    return jsonify(db.get_achievements())


# ==========================================
# RUN
# ==========================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  AI PERSONAL TRAINER - Web Dashboard")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)
