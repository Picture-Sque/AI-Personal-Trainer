import sys
import os
sys.path.append("team_b_application")
import database as db

def main():
    print("Testing database module...")
    # Initialize DB (creates workouts.db if it doesn't exist)
    db.init_db()
    
    # Save a workout
    db.save_workout(
        exercise="Squat",
        reps=10,
        duration=15.5,
        avg_rep_speed=1.5,
        fatigue_level=0,
        form_warnings=1
    )
    
    # Save another workout to trigger an achievement (First Step)
    db.save_workout(
        exercise="Bicep Curl",
        reps=15,
        duration=20.0,
        avg_rep_speed=1.3,
        fatigue_level=1,
        form_warnings=0
    )
    
    # Retrieve workouts
    workouts = db.get_recent_workouts(5)
    print(f"Retrieved {len(workouts)} recent workouts.")
    assert len(workouts) >= 2
    
    # Check stats
    stats = db.get_dashboard_stats()
    print("Stats:", stats)
    assert stats['total_workouts'] >= 2
    assert stats['total_reps'] >= 25
    
    # Check achievements
    achievements = db.get_achievements()
    print("Achievements unlocked:", [a['name'] for a in achievements])
    assert len(achievements) >= 1
    
    # Check analytics
    analytics = db.get_analytics_data()
    print("Analytics retrieved successfully.")
    
    print("✅ All database tests passed!")
    sys.exit(0)

if __name__ == '__main__':
    main()
