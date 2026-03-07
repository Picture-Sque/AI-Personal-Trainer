import sys
sys.path.append("team_b_application")
from logic import Squat, BicepCurl, JumpingJacks, ShoulderPress, Lunge, PushUp, HighKnees, LateralRaise

def test_exercise(name, cls, down_angle, up_angle, half_rep_multiplier=1):
    print(f"Testing {name}...")
    trainer = cls()
    
    # Do 5 reps
    for _ in range(5 * half_rep_multiplier):
        # State DOWN
        trainer.process(down_angle)
        # State UP
        rep_complete, feedback, angle = trainer.process(up_angle)

    if trainer.reps == 5:
        print(f"✅ {name} passed (5 reps completed).")
        return True
    else:
        print(f"❌ {name} failed. Reached {trainer.reps} reps.")
        return False

def main():
    success = True
    # Squat (Stand -> Squat -> Stand)
    # stage: UP -> DOWN (knee < 90) -> UP (knee > 160)
    success &= test_exercise("Squat", Squat, 80, 170)
    
    # Bicep Curl (Down -> Curl -> Down)
    # stage: DOWN -> UP (elbow < 40) -> DOWN (elbow > 160)
    success &= test_exercise("Bicep Curl", BicepCurl, 30, 170)
    
    # Jumping Jacks (Down -> Up -> Down)
    # stage: DOWN -> UP (arms > 140) -> DOWN (arms < 60)
    success &= test_exercise("Jumping Jacks", JumpingJacks, 150, 40)
    
    # Shoulder Press (Down -> Up -> Down)
    # stage: DOWN -> UP (elbow > 160) -> DOWN (elbow < 90)
    success &= test_exercise("Shoulder Press", ShoulderPress, 170, 80)
    
    # Lunge (Up -> Down -> Up)
    # stage: UP -> DOWN (knee < 100) -> UP (knee > 160)
    success &= test_exercise("Lunge", Lunge, 90, 170)
    
    # Push Up (Up -> Down -> Up)
    # stage: UP -> DOWN (elbow < 90) -> UP (elbow > 160)
    success &= test_exercise("Push Up", PushUp, 80, 170)
    
    # High Knees (Down -> Knees Up -> Down)
    # stage: DOWN -> UP (hip < 70) -> DOWN (hip > 140)
    # Every 2 half-reps = 1 full rep.
    success &= test_exercise("High Knees", HighKnees, 60, 160, half_rep_multiplier=2)
    
    # Lateral Raise (Down -> Up -> Down)
    # stage: DOWN -> UP (shoulder > 80) -> DOWN (shoulder < 30)
    success &= test_exercise("Lateral Raise", LateralRaise, 90, 20)
    
    if success:
        print("All tests passed successfully!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
