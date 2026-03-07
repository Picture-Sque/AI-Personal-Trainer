import cv2
import time
import numpy as np

# IMPORT THE MODULES
from vision_engine import VisionEngine  # The Eyes
from logic import Squat, BicepCurl, JumpingJacks, ShoulderPress, Lunge, PushUp, HighKnees, LateralRaise  # The Brain
from feedback import speak              # The Voice 🔊

def main():
    vision = VisionEngine()
    
    # --- OUTER LOOP: THE MAIN MENU ---
    while True:
        print("\n=========================================")
        print("       AI PERSONAL TRAINER (TEAM B)      ")
        print("=========================================")
        print("1. Squat (Tracks Knee & Back)")
        print("2. Bicep Curl (Tracks Elbow)")
        print("3. Jumping Jacks (Tracks Arm Raises)")
        print("4. Shoulder Press (Tracks Arm Extension)")
        print("5. Lunge (Tracks Knee Depth)")
        print("6. Push-Up (Tracks Elbow & Body Line)")
        print("7. High Knees (Tracks Knee Height)")
        print("8. Lateral Raise (Tracks Arm Raise)")
        print("q. Exit Application")
        
        choice = input("\nSelect Option: ")

        if choice.lower() == 'q':
            print("Exiting... Stay fit!")
            break
        elif choice == '1':
            trainer = Squat()
        elif choice == '2':
            trainer = BicepCurl()
        elif choice == '3':
            trainer = JumpingJacks()
        elif choice == '4':
            trainer = ShoulderPress()
        elif choice == '5':
            trainer = Lunge()
        elif choice == '6':
            trainer = PushUp()
        elif choice == '7':
            trainer = HighKnees()
        elif choice == '8':
            trainer = LateralRaise()
        else:
            print("Invalid selection. Try again.")
            continue
        
        print(f"Starting {trainer.name}...")
        speak(f"Starting {trainer.name} session")
        
        # 1. SETUP CAMERA FOR SESSION
        cap = cv2.VideoCapture(0)
        
        # --- INNER LOOP: THE EXERCISE SESSION ---
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            # --- VISION ---
            image, landmarks = vision.process_frame(frame)
            
            # --- LOGIC ---
            feedback_text = ""
            
            if landmarks:
                # Process Reps
                rep_complete, feedback_text, angle = trainer.process(landmarks)

                # --- UI DRAWING ---
                cv2.rectangle(image, (0,0), (350, 120), (245, 117, 16), -1)
                cv2.putText(image, trainer.name.upper(), (15, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 1, cv2.LINE_AA)
                cv2.putText(image, str(trainer.reps), (20, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                cv2.putText(image, "REPS", (20, 115), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                cv2.putText(image, trainer.stage, (150, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Angle: {int(angle)}", (15, 145), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)

                # --- AUDIO & TEXT FEEDBACK ---
                if feedback_text:
                    cv2.rectangle(image, (0, 420), (640, 480), (0,0,0), -1)
                    
                    text_color = (0, 255, 0) # Green
                    if "menu" in feedback_text.lower() or "straighten" in feedback_text.lower():
                        text_color = (0, 0, 255) # Red
                        
                    cv2.putText(image, feedback_text, (10, 460), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv2.LINE_AA)
                    
                    speak(feedback_text)
                
                # --- GAME OVER CHECK (Returns to Menu) ---
                if trainer.game_over:
                    cv2.putText(image, "SESSION OVER", (130, 250), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5, cv2.LINE_AA)
                    cv2.imshow('AI Trainer', image)
                    cv2.waitKey(4000) # Wait 4 seconds so user reads the message
                    break # Breaks the inner loop, taking us back to the Main Menu

            cv2.imshow('AI Trainer', image)

            # Manual exit to menu
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # CLEANUP SESSION BEFORE GOING BACK TO MENU
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()