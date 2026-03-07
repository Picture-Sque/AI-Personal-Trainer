"""
Database Manager for AI Personal Trainer.
Handles workout history storage and analytics queries using SQLite.
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'workouts.db')


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise TEXT NOT NULL,
            reps INTEGER NOT NULL,
            duration_seconds REAL NOT NULL,
            avg_rep_speed REAL,
            fatigue_level INTEGER DEFAULT 0,
            form_warnings INTEGER DEFAULT 0,
            calories_burned REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def save_workout(exercise, reps, duration, avg_rep_speed=0, fatigue_level=0, form_warnings=0):
    """Save a completed workout session."""
    # Rough calorie estimate: ~0.5 cal per rep (varies by exercise)
    calorie_rates = {
        'Squat': 0.6, 'Bicep Curl': 0.3, 'Jumping Jacks': 0.7,
        'Shoulder Press': 0.4, 'Lunge': 0.5, 'Push Up': 0.5,
        'High Knees': 0.8, 'Lateral Raise': 0.3
    }
    cal_rate = calorie_rates.get(exercise, 0.5)
    calories = reps * cal_rate

    conn = get_connection()
    conn.execute(
        '''INSERT INTO workouts (exercise, reps, duration_seconds, avg_rep_speed, 
           fatigue_level, form_warnings, calories_burned) VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (exercise, reps, duration, avg_rep_speed, fatigue_level, form_warnings, calories)
    )
    conn.commit()
    conn.close()

    # Check for new achievements
    check_achievements()


def get_recent_workouts(limit=10):
    """Get the most recent workouts."""
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM workouts ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_workouts():
    """Get all workouts for history page."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM workouts ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_stats():
    """Get aggregate stats for the dashboard."""
    conn = get_connection()
    c = conn.cursor()

    total = c.execute('SELECT COUNT(*) FROM workouts').fetchone()[0]
    total_reps = c.execute('SELECT COALESCE(SUM(reps), 0) FROM workouts').fetchone()[0]
    total_calories = c.execute('SELECT COALESCE(SUM(calories_burned), 0) FROM workouts').fetchone()[0]

    # This week
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    this_week = c.execute(
        'SELECT COUNT(*) FROM workouts WHERE created_at >= ?', (week_ago,)
    ).fetchone()[0]

    # Streak calculation
    streak = calculate_streak(c)

    conn.close()
    return {
        'total_workouts': total,
        'this_week': this_week,
        'total_reps': total_reps,
        'calories_burned': round(total_calories, 1),
        'streak': streak
    }


def calculate_streak(cursor):
    """Calculate consecutive workout days."""
    rows = cursor.execute(
        "SELECT DISTINCT DATE(created_at) as d FROM workouts ORDER BY d DESC"
    ).fetchall()

    if not rows:
        return 0

    streak = 0
    today = datetime.now().date()

    for row in rows:
        workout_date = datetime.strptime(row[0], '%Y-%m-%d').date()
        expected = today - timedelta(days=streak)
        if workout_date == expected:
            streak += 1
        elif workout_date == expected - timedelta(days=1):
            streak += 1
        else:
            break

    return streak


def get_analytics_data():
    """Get data for the analytics page charts."""
    conn = get_connection()
    c = conn.cursor()

    # Weekly reps (last 7 days)
    weekly = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_label = (datetime.now() - timedelta(days=i)).strftime('%a')
        reps = c.execute(
            "SELECT COALESCE(SUM(reps), 0) FROM workouts WHERE DATE(created_at) = ?", (day,)
        ).fetchone()[0]
        weekly.append({'day': day_label, 'reps': reps})

    # Exercise breakdown
    breakdown = c.execute(
        "SELECT exercise, COUNT(*) as count, SUM(reps) as total_reps FROM workouts GROUP BY exercise"
    ).fetchall()
    exercise_breakdown = [{'exercise': r[0], 'count': r[1], 'total_reps': r[2]} for r in breakdown]

    # Personal records (max reps per exercise)
    records = c.execute(
        "SELECT exercise, MAX(reps) as max_reps FROM workouts GROUP BY exercise"
    ).fetchall()
    personal_records = [{'exercise': r[0], 'max_reps': r[1]} for r in records]

    # Monthly trend (last 30 days)
    monthly = []
    for i in range(29, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_short = (datetime.now() - timedelta(days=i)).strftime('%d')
        reps = c.execute(
            "SELECT COALESCE(SUM(reps), 0) FROM workouts WHERE DATE(created_at) = ?", (day,)
        ).fetchone()[0]
        monthly.append({'day': day_short, 'reps': reps})

    conn.close()
    return {
        'weekly': weekly,
        'exercise_breakdown': exercise_breakdown,
        'personal_records': personal_records,
        'monthly': monthly
    }


def get_achievements():
    """Get all unlocked achievements."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM achievements ORDER BY unlocked_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def check_achievements():
    """Check and unlock new achievements."""
    conn = get_connection()
    c = conn.cursor()

    total = c.execute('SELECT COUNT(*) FROM workouts').fetchone()[0]
    total_reps = c.execute('SELECT COALESCE(SUM(reps), 0) FROM workouts').fetchone()[0]

    milestones = [
        (1, 'First Step', 'Completed your first workout', '🏁'),
        (5, 'Getting Started', 'Completed 5 workouts', '⭐'),
        (10, 'Dedicated', 'Completed 10 workouts', '🔥'),
        (25, 'Committed', 'Completed 25 workouts', '💪'),
        (50, 'Beast Mode', 'Completed 50 workouts', '🦁'),
        (100, 'Century', 'Completed 100 workouts', '💯'),
    ]

    rep_milestones = [
        (50, 'Half Century Reps', 'Performed 50 total reps', '🎯'),
        (100, 'Rep Machine', 'Performed 100 total reps', '⚡'),
        (500, 'Rep Legend', 'Performed 500 total reps', '🏆'),
        (1000, 'Rep God', 'Performed 1000 total reps', '👑'),
    ]

    for threshold, name, desc, icon in milestones:
        if total >= threshold:
            try:
                c.execute(
                    'INSERT INTO achievements (name, description, icon) VALUES (?, ?, ?)',
                    (name, desc, icon)
                )
            except sqlite3.IntegrityError:
                pass

    for threshold, name, desc, icon in rep_milestones:
        if total_reps >= threshold:
            try:
                c.execute(
                    'INSERT INTO achievements (name, description, icon) VALUES (?, ?, ?)',
                    (name, desc, icon)
                )
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()


# Initialize on import
init_db()
