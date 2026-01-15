import time
from logic import Squat, BicepCurl
from feedback import speak

def main():
    while True:
        print("\n=========================================")
        print("       AI PERSONAL TRAINER (TEAM B)      ")
        print("=========================================")
        print("1. Start Squat Session")
        print("2. Start Bicep Curl Session")
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
                # --- INPUT PARSING (Handles "80" OR "80, 50") ---
                if "," in user_input:
                    # Split "80, 50" into [80.0, 50.0]
                    parts = user_input.split(",")
                    input_data = [float(parts[0]), float(parts[1])]
                else:
                    # Normal single number
                    input_data = float(user_input)

                # --- PROCESS THE REP ---
                rep_complete, feedback_text, _ = trainer.process(input_data)
                
                # --- SPEAK FEEDBACK ---
                if feedback_text:
                    print(f"🔊 COACH: '{feedback_text}'")
                    speak(feedback_text)
                
                # --- CHECK FOR GAME OVER (RED LIGHT) ---
                if trainer.game_over:
                    print("\n🛑 SESSION TERMINATED: FATIGUE DETECTED")
                    print(f"Final Score: {trainer.reps} Reps")
                    print("Returning to menu in 4 seconds...")
                    time.sleep(4) 
                    break # Break inner loop -> Main Menu
                    
            except ValueError:
                print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()