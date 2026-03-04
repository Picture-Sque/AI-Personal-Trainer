import time
import random
import numpy as np
from utils import calculate_angle

# ==========================================
# PARENT CLASS: THE BRAIN 🧠
# ==========================================
class Exercise:
    def __init__(self, name):
        self.name = name
        self.reps = 0
        self.game_over = False 
        
        self.start_time = 0
        self.rep_durations = [] 
        self.baseline_speed = 0
        
        self.fatigue_warning = 1.3  # Yellow
        self.fatigue_failure = 1.8  # Red

    def start_rep_timer(self):
        self.start_time = time.time()

    def stop_rep_timer(self):
        end_time = time.time()
        duration = end_time - self.start_time
        if duration < 0.1: duration = 0.1
        self.rep_durations.append(duration)
        return duration

    def get_fatigue_level(self, current_duration):
        if self.reps <= 3:
            self.baseline_speed = sum(self.rep_durations) / len(self.rep_durations)
            return 0 
        else:
            yellow_limit = self.baseline_speed * self.fatigue_warning
            red_limit = self.baseline_speed * self.fatigue_failure
            
            if current_duration > red_limit:
                return 2 
            elif current_duration > yellow_limit:
                return 1 
            else:
                return 0 

# ==========================================
# CHILD CLASS 1: SQUAT 🏋️‍♂️
# ==========================================
class Squat(Exercise):
    def __init__(self):
        super().__init__("Squat")
        self.stage = "UP"
        self.last_speech_time = 0
        self.speech_cooldown = 5.0 
        
        self.phrases_bad_back = [
            "You are leaning too far forward. Please straighten your back.",
            "Your chest is dropping down. Keep your chest lifted up."
        ]
        self.phrases_push = [
            "You are slowing down. Come on, push through the pain!",
            "Don't give up now. Maintain your speed!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        
        if isinstance(landmarks, (int, float)):
            knee_angle = landmarks
            back_angle = 100 
        else:
            shoulder = landmarks['LEFT_SHOULDER']
            hip = landmarks['LEFT_HIP']
            knee = landmarks['LEFT_KNEE']
            ankle = landmarks['LEFT_ANKLE']
            knee_angle = calculate_angle(hip, knee, ankle)
            back_angle = calculate_angle(shoulder, hip, knee)

        current_time = time.time()

        if knee_angle < 120 and back_angle < 60:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_bad_back)
                self.last_speech_time = current_time

        if knee_angle < 90:
            if self.stage == "UP":
                self.stage = "DOWN"
                self.start_rep_timer()
        
        if knee_angle > 160:
            if self.stage == "DOWN":
                self.stage = "UP"
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                self.reps += 1
                
                if fatigue_level == 2:
                    feedback = self.phrases_stop
                    self.game_over = True 
                else:
                    feedback = f"{self.reps}. {random.choice(self.phrases_push)}" if fatigue_level == 1 else str(self.reps)
                rep_complete = True

        return rep_complete, feedback, knee_angle

# ==========================================
# CHILD CLASS 2: BICEP CURL 💪
# ==========================================
class BicepCurl(Exercise):
    def __init__(self):
        super().__init__("Bicep Curl")
        self.stage = "DOWN"
        
        self.phrases_push = [
            "Lift it all the way up. Don't stop now!",
            "You are getting tired, but stay strong. Keep curling!",
            "Focus on the squeeze. Do not let the weight drop."
        ]
        
        # RESTORED: All of your original form correction phrases
        self.phrases_swing = [
            "Do not swing your elbow. Keep it fixed at your side.",
            "You are using your shoulder. Focus only on the bicep.",
            "Stop moving your upper arm. Lock your elbow in place."
        ]
        
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."
        
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()
        
        if isinstance(landmarks, (int, float)):
            elbow_angle = landmarks
            shoulder_angle = 10 
        else:
            shoulder = landmarks['LEFT_SHOULDER']
            elbow = landmarks['LEFT_ELBOW']
            wrist = landmarks['LEFT_WRIST']
            hip = landmarks['LEFT_HIP'] 
            
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            shoulder_angle = calculate_angle(hip, shoulder, elbow)
            
        # 1. CHEAT DETECTION: Swinging Elbow
        if shoulder_angle > 30:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_swing)
                self.last_speech_time = current_time
                print(f" -> COACH: {feedback}") # RESTORED: Terminal logging

        # 2. REP LOGIC: Going UP
        if elbow_angle < 50:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()
                print(f" -> {self.name} UP")
                
        # 3. REP LOGIC: Going DOWN
        if elbow_angle > 160:
            if self.stage == "UP":
                self.stage = "DOWN"
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                self.reps += 1
                
                rep_feedback = "" 
                
                if fatigue_level == 2:
                    rep_feedback = self.phrases_stop
                    self.game_over = True 
                    print(f" -> FATIGUE WARNING (Rep {self.reps})")
                else:
                    if fatigue_level == 1:
                        rep_feedback = f"{self.reps}. {random.choice(self.phrases_push)}"
                    else:
                        rep_feedback = str(self.reps)
                    print(f" -> DOWN (Rep {self.reps})")
                
                # FIXED: Only show the rep count if the AI isn't currently yelling at you to fix your posture!
                if feedback is None:
                    feedback = rep_feedback
                
                rep_complete = True

        return rep_complete, feedback, elbow_angle

# ==========================================
# CHILD CLASS 3: JUMPING JACKS 🏃‍♂️ (STRICT ANTI-CHEAT)
# ==========================================
class JumpingJacks(Exercise):
    def __init__(self):
        super().__init__("Jumping Jacks")
        self.stage = "DOWN"
        
        # New targeted audio warnings
        self.phrases_lazy_legs = [
            "Jump symmetrically! Both feet must move.",
            "Don't lean! Keep your body centered when jumping."
        ]
        self.phrases_bent_knees = [
            "Keep your legs straight!",
            "Do not bend your knees too much."
        ]
        self.phrases_push = [
            "Keep the rhythm going! Great job.",
            "You're doing great, keep that heart rate up!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."
        
        self.last_speech_time = 0
        self.speech_cooldown = 3.0

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()
        
        if isinstance(landmarks, (int, float)):
            # Terminal simulation mock variables
            arm_angle = landmarks
            is_wide_stance = True if landmarks > 140 else False
            is_symmetric = True
            is_narrow_stance = True if landmarks < 60 else False
            l_knee_angle = 180
            r_knee_angle = 180
        else:
            # 1. GET ALL JOINTS
            l_shoulder = landmarks['LEFT_SHOULDER']
            r_shoulder = landmarks['RIGHT_SHOULDER']
            l_wrist = landmarks['LEFT_WRIST']
            
            l_hip = landmarks['LEFT_HIP']
            r_hip = landmarks['RIGHT_HIP']
            
            l_knee = landmarks['LEFT_KNEE']
            r_knee = landmarks['RIGHT_KNEE']
            l_ankle = landmarks['LEFT_ANKLE']
            r_ankle = landmarks['RIGHT_ANKLE']
            
            # 2. CALCULATE ARM & KNEE ANGLES
            arm_angle = calculate_angle(l_hip, l_shoulder, l_wrist)
            
            # Knee straightness (Should be near 180)
            l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            
            # 3. SPATIAL SYMMETRY CHECK (The One-Leg Cheat Fix)
            # x-coordinates are at index 0. We measure distances across the screen.
            shoulder_width = abs(l_shoulder[0] - r_shoulder[0])
            if shoulder_width < 0.05: shoulder_width = 0.05 # Prevent glitch if turned sideways
            
            ankle_width = abs(l_ankle[0] - r_ankle[0])
            
            # Find the midpoint of the hips and the midpoint of the ankles
            hip_center_x = (l_hip[0] + r_hip[0]) / 2.0
            ankle_center_x = (l_ankle[0] + r_ankle[0]) / 2.0
            
            # Calculate how far off-center the feet are compared to the torso
            symmetry_offset = abs(hip_center_x - ankle_center_x)
            
            # Strict Boolean Triggers
            is_wide_stance = ankle_width > (shoulder_width * 1.5) # Feet must be wider than shoulders
            is_narrow_stance = ankle_width < (shoulder_width * 1.2) # Feet must come back in
            is_symmetric = symmetry_offset < (shoulder_width * 0.5) # Center of gravity must stay balanced

        # 4. CHEAT DETECTION
        
        # A. Bent Knees check
        if l_knee_angle < 150 or r_knee_angle < 150:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_bent_knees)
                self.last_speech_time = current_time

        # B. One-Leg / Asymmetrical Jump Check
        elif arm_angle > 140 and is_wide_stance and not is_symmetric:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_lazy_legs)
                self.last_speech_time = current_time

        # 5. REP LOGIC 
        
        # JUMPING OUT (Going UP)
        # ALL conditions must be met: Arms high, legs wide, balanced center, knees straight
        if arm_angle > 140 and is_wide_stance and is_symmetric and l_knee_angle > 150 and r_knee_angle > 150:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()
                
        # JUMPING IN (Going DOWN & Counting Rep)
        # Arms must drop and legs must come back close together
        if arm_angle < 60 and is_narrow_stance:
            if self.stage == "UP":
                self.stage = "DOWN"
                
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                
                self.reps += 1
                
                if fatigue_level == 2:
                    feedback = self.phrases_stop
                    self.game_over = True 
                else:
                    if fatigue_level == 1:
                        feedback = f"{self.reps}. {random.choice(self.phrases_push)}"
                    else:
                        feedback = str(self.reps)
                
                rep_complete = True

        return rep_complete, feedback, arm_angle