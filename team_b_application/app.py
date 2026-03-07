import time
from logic import Squat, BicepCurl, JumpingJacks, ShoulderPress, Lunge, PushUp, HighKnees, LateralRaise
from feedback import speak

def main():
    while True:
        print("\n=========================================")
        print("       AI PERSONAL TRAINER (TEAM B)      ")
        print("=========================================")
        print("1. Start Squat Session")
        print("2. Start Bicep Curl Session")
        print("3. Start Jumping Jacks Session")
        print("4. Start Shoulder Press Session")
        print("5. Start Lunge Session")
        print("6. Start Push-Up Session")
        print("7. Start High Knees Session")
        print("8. Start Lateral Raise Session")
        print("q. Exit Application")
        
        choice = input("\nSelect Option: ")
        
        if choice.lower() == 'q':
            print("Exiting... Stay fit!")
            break
        
        # 1. INITIALIZE THE TRAINER
        trainer = None
        if choice == '1':
            trainer = Squat()
            print("\n--- SQUAT SESSION STARTED ---")
            print("Tip 1: Type 170 (Stand) -> 80 (Squat)")
            print("Tip 2 (Back Check): Type '80, 50' to sim Squat with Bad Back")
        elif choice == '2':
            trainer = BicepCurl()
            print("\n--- BICEP CURL SESSION STARTED ---")
            print("Tip: Type 170 (Down) -> 25 (Curl Up)")
        elif choice == '3':
            trainer = JumpingJacks()
            print("\n--- JUMPING JACKS SESSION STARTED ---")
            print("Tip: Type 150 (Arms Up) -> 40 (Arms Down)")
        elif choice == '4':
            trainer = ShoulderPress()
            print("\n--- SHOULDER PRESS SESSION STARTED ---")
            print("Tip: Type 170 (Arms Up) -> 70 (Arms Down)")
        elif choice == '5':
            trainer = Lunge()
            print("\n--- LUNGE SESSION STARTED ---")
            print("Tip: Type 170 (Standing) -> 80 (Lunge Down)")
        elif choice == '6':
            trainer = PushUp()
            print("\n--- PUSH-UP SESSION STARTED ---")
            print("Tip: Type 170 (Arms Straight) -> 70 (Arms Bent)")
        elif choice == '7':
            trainer = HighKnees()
            print("\n--- HIGH KNEES SESSION STARTED ---")
            print("Tip: Type 60 (Knee Up) -> 160 (Knee Down)")
        elif choice == '8':
            trainer = LateralRaise()
            print("\n--- LATERAL RAISE SESSION STARTED ---")
            print("Tip: Type 90 (Arms Up) -> 20 (Arms Down)")
        else:
            print("Invalid selection.")
            continue 

        # Say hello
        speak(f"Starting {trainer.name} session.")

        # 2. THE EXERCISE LOOP
        while True:
            user_input = input(f"\n[{trainer.name}] Enter Angle ('b' to back): ")
            
            # Allow user to quit manually
            if user_input.lower() == 'b':
                print("Returning to Main Menu...")
                break
                
            try:
                # --- INPUT PARSING ---
                if "," in user_input:
                    parts = user_input.split(",")
                    input_data = [float(parts[0]), float(parts[1])]
                else:
                    input_data = float(user_input)

                # --- PROCESS THE REP ---
                rep_complete, feedback_text, _ = trainer.process(input_data)
                
                # --- SPEAK FEEDBACK ---
                if feedback_text:
                    print(f"🔊 COACH: '{feedback_text}'")
                    speak(feedback_text)
                
                # --- CHECK FOR GAME OVER ---
                if trainer.game_over:
                    print("\n🛑 SESSION TERMINATED: FATIGUE DETECTED")
                    print(f"Final Score: {trainer.reps} Reps")
                    print("Returning to menu in 4 seconds...")
                    time.sleep(4) 
                    break # Breaks inner loop -> Back to Main Menu
                    
            except ValueError:
                print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()