import time
from logic import RepCounter
from feedback import speak

def main():
    print("--- AI GYM TRAINER (TEAM B PROTOTYPE) ---")
    print("Type an angle to test logic (e.g., 170 for standing, 80 for squat).")
    print("Type 'q' to quit.\n")

    # Initialize KD's Logic
    counter = RepCounter()
    
    # Say hello (Shakki's Voice)
    speak("System Ready. Let's workout.")

    while True:
        user_input = input("Enter Knee Angle: ")
        
        if user_input.lower() == 'q':
            break
            
        try:
            angle = float(user_input)
            
            # Pass data to KD's Brain
            new_rep_completed = counter.process_angle(angle)
            
            # If rep is done, trigger Shakki's Voice
            if new_rep_completed:
                speak(str(counter.reps))
                
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()