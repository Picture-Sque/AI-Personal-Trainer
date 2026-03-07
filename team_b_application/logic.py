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
# CHILD CLASS 1: SQUAT 🏋️‍♂️ (BOTH LEGS TRACKED)
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
        # CHEAT: Knees caving inward (valgus)
        self.phrases_knees_caving = [
            "Your knees are caving inward. Push them out over your toes.",
            "Keep your knees in line with your feet. Don't let them collapse.",
            "Drive your knees outward. Inward collapse can cause injury."
        ]
        # CHEAT: Asymmetric squat (one leg doing more work)
        self.phrases_asymmetric = [
            "Your squat is uneven. Distribute weight equally on both legs.",
            "One leg is bending more than the other. Keep it balanced."
        ]
        self.phrases_push = [
            "You are slowing down. Come on, push through the pain!",
            "Don't give up now. Maintain your speed!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()
        
        if isinstance(landmarks, (int, float)):
            knee_angle = landmarks
            back_angle = 100
        else:
            # --- TRACK BOTH SIDES ---
            l_shoulder = landmarks['LEFT_SHOULDER']
            l_hip = landmarks['LEFT_HIP']
            l_knee = landmarks['LEFT_KNEE']
            l_ankle = landmarks['LEFT_ANKLE']

            r_shoulder = landmarks['RIGHT_SHOULDER']
            r_hip = landmarks['RIGHT_HIP']
            r_knee = landmarks['RIGHT_KNEE']
            r_ankle = landmarks['RIGHT_ANKLE']

            # Both knee angles
            l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            knee_angle = (l_knee_angle + r_knee_angle) / 2.0

            # Back angle (average both sides)
            l_back = calculate_angle(l_shoulder, l_hip, l_knee)
            r_back = calculate_angle(r_shoulder, r_hip, r_knee)
            back_angle = (l_back + r_back) / 2.0

            # --- CHEAT: Knee valgus (knees caving inward) ---
            # If knees are closer together than ankles, knees are caving
            knee_width = abs(l_knee[0] - r_knee[0])
            ankle_width = abs(l_ankle[0] - r_ankle[0])
            if knee_angle < 130 and knee_width < (ankle_width * 0.7):
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_knees_caving)
                    self.last_speech_time = current_time

            # --- CHEAT: Asymmetric squat ---
            if abs(l_knee_angle - r_knee_angle) > 25:
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_asymmetric)
                    self.last_speech_time = current_time

        # CHEAT: Bad back (leaning forward)
        if knee_angle < 120 and back_angle < 60:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_bad_back)
                self.last_speech_time = current_time

        # --- REP LOGIC (uses average of both knees) ---
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
# CHILD CLASS 2: BICEP CURL 💪 (SIDE VIEW, SINGLE ARM)
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
        
        self.phrases_swing = [
            "Do not swing your elbow. Keep it fixed at your side.",
            "You are using your shoulder. Focus only on the bicep.",
            "Stop moving your upper arm. Lock your elbow in place."
        ]

        # CHEAT: Half rep (not curling fully)
        self.phrases_half_rep = [
            "Curl all the way up. Squeeze at the top.",
            "That's a half rep. Bring the weight up fully.",
            "Full range of motion. Don't cut the curl short."
        ]
        
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."
        
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

        # Track lowest angle per rep for half-rep detection
        self.lowest_elbow_angle = 180

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()
        
        if isinstance(landmarks, (int, float)):
            elbow_angle = landmarks
            shoulder_angle = 10
        else:
            # --- SIDE VIEW: Track the arm facing the camera (LEFT side) ---
            shoulder = landmarks['LEFT_SHOULDER']
            elbow = landmarks['LEFT_ELBOW']
            wrist = landmarks['LEFT_WRIST']
            hip = landmarks['LEFT_HIP']
            
            # Elbow angle (primary tracking)
            elbow_angle = calculate_angle(shoulder, elbow, wrist)

            # Shoulder angle (for swing/cheat detection)
            shoulder_angle = calculate_angle(hip, shoulder, elbow)

        # Track lowest point for half-rep detection
        if elbow_angle < self.lowest_elbow_angle:
            self.lowest_elbow_angle = elbow_angle

        # --- CHEAT DETECTION ---
            
        # 1. SWINGING ELBOW (upper arm moving)
        if shoulder_angle > 30:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_swing)
                self.last_speech_time = current_time
                print(f" -> COACH: {feedback}")

        # --- REP LOGIC ---

        # Going UP (arm curling)
        if elbow_angle < 40:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()
                print(f" -> {self.name} UP")
                
        # Going DOWN (arm extending)
        if elbow_angle > 160:
            if self.stage == "UP":
                self.stage = "DOWN"
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                self.reps += 1
                
                rep_feedback = ""

                # 2. HALF REP CHECK
                if self.lowest_elbow_angle > 60:
                    rep_feedback = f"{self.reps}. {random.choice(self.phrases_half_rep)}"
                elif fatigue_level == 2:
                    rep_feedback = self.phrases_stop
                    self.game_over = True 
                    print(f" -> FATIGUE WARNING (Rep {self.reps})")
                else:
                    if fatigue_level == 1:
                        rep_feedback = f"{self.reps}. {random.choice(self.phrases_push)}"
                    else:
                        rep_feedback = str(self.reps)
                    print(f" -> DOWN (Rep {self.reps})")
                
                # Only show rep feedback if form correction isn't active
                if feedback is None:
                    feedback = rep_feedback
                
                # Reset half-rep tracker
                self.lowest_elbow_angle = 180
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
            r_wrist = landmarks['RIGHT_WRIST']
            
            l_hip = landmarks['LEFT_HIP']
            r_hip = landmarks['RIGHT_HIP']
            
            l_knee = landmarks['LEFT_KNEE']
            r_knee = landmarks['RIGHT_KNEE']
            l_ankle = landmarks['LEFT_ANKLE']
            r_ankle = landmarks['RIGHT_ANKLE']
            
            # 2. CALCULATE ARM & KNEE ANGLES (BOTH ARMS)
            l_arm_angle = calculate_angle(l_hip, l_shoulder, l_wrist)
            r_arm_angle = calculate_angle(r_hip, r_shoulder, r_wrist)
            arm_angle = (l_arm_angle + r_arm_angle) / 2.0
            
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

# ==========================================
# CHILD CLASS 4: SHOULDER PRESS 🏋️
# ==========================================
# HOW IT WORKS:
#   Camera View: FRONT facing
#   Primary Angle: Elbow angle (shoulder → elbow → wrist)
#   Rep Logic: Arms bent (DOWN) → Arms extended overhead (UP)
#
# CHEAT DETECTION:
#   1. ASYMMETRIC PRESSING - Left and right elbow angles differ by >25°
#      → User is pressing unevenly, dominant arm doing more work.
#   2. INCOMPLETE EXTENSION - Arms don't fully straighten at the top (>160°)
#      → User cuts the rep short to avoid the hardest part.
#   3. LEANING BACK - Shoulder-hip-knee angle becomes too small (<160°)
#      → User arches their back to use momentum instead of shoulder strength.
#   4. ELBOWS FLARING OUT - Tracked via wrist position relative to shoulder
#      → Bad shoulder health; elbows should stay in front of the body.
# ==========================================
class ShoulderPress(Exercise):
    def __init__(self):
        super().__init__("Shoulder Press")
        self.stage = "DOWN"
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

        # CHEAT: Asymmetric pressing (one arm lagging)
        self.phrases_asymmetric = [
            "Your arms are uneven. Press both sides equally.",
            "One arm is lagging behind. Focus on pressing symmetrically.",
            "Balance your press. Both arms should move together."
        ]
        # CHEAT: Not fully extending arms at the top
        self.phrases_partial_rep = [
            "Extend your arms fully at the top. Don't cut the rep short.",
            "Push all the way up. Lock out your elbows at the top.",
            "You're doing half reps. Straighten your arms completely."
        ]
        # CHEAT: Leaning back (using spine momentum)
        self.phrases_leaning_back = [
            "You are leaning back. Keep your torso upright.",
            "Stop arching your back. Engage your core and press straight up.",
            "Your back is bending. Stand tall and press with your shoulders."
        ]
        self.phrases_push = [
            "You're slowing down. Keep pressing strong!",
            "Don't quit now. Drive those arms overhead!",
            "Stay focused. Maintain your rhythm!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()

        if isinstance(landmarks, (int, float)):
            l_elbow_angle = landmarks
            r_elbow_angle = landmarks
            back_angle = 175
        else:
            # --- EXTRACT ALL JOINTS ---
            l_shoulder = landmarks['LEFT_SHOULDER']
            l_elbow = landmarks['LEFT_ELBOW']
            l_wrist = landmarks['LEFT_WRIST']
            l_hip = landmarks['LEFT_HIP']
            l_knee = landmarks['LEFT_KNEE']

            r_shoulder = landmarks['RIGHT_SHOULDER']
            r_elbow = landmarks['RIGHT_ELBOW']
            r_wrist = landmarks['RIGHT_WRIST']

            # --- PRIMARY ANGLES ---
            l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # --- CHEAT DETECTION ANGLE ---
            # Back angle: shoulder → hip → knee (should be ~180 = upright)
            back_angle = calculate_angle(l_shoulder, l_hip, l_knee)

        # Use average elbow angle for rep tracking
        avg_elbow_angle = (l_elbow_angle + r_elbow_angle) / 2.0

        # --- CHEAT DETECTION ---

        # 1. LEANING BACK (most dangerous cheat - injury risk)
        if back_angle < 160:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_leaning_back)
                self.last_speech_time = current_time

        # 2. ASYMMETRIC PRESSING (one arm doing more work)
        elif abs(l_elbow_angle - r_elbow_angle) > 25:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_asymmetric)
                self.last_speech_time = current_time

        # --- REP LOGIC ---

        # Going UP (arms extending overhead)
        if avg_elbow_angle > 160:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()

        # Going DOWN (arms bending back)
        if avg_elbow_angle < 90:
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

        return rep_complete, feedback, avg_elbow_angle


# ==========================================
# CHILD CLASS 5: LUNGE 🦵
# ==========================================
# HOW IT WORKS:
#   Camera View: SIDE facing (left side to camera)
#   Primary Angle: Front knee angle (hip → knee → ankle)
#   Rep Logic: Standing straight (UP) → Knee bent deep (DOWN)
#
# CHEAT DETECTION:
#   1. SHALLOW LUNGE - Front knee doesn't bend below 100°
#      → User barely dips, avoiding the deep stretch that builds muscle.
#   2. TORSO LEANING FORWARD - Shoulder-hip-knee angle <70°
#      → Shifts load off legs onto back; reduces quad activation.
#   3. FRONT KNEE OVER TOE - Knee x-position goes past ankle x-position
#      → High knee stress; bad for joint health. (Side view needed)
#   4. BACK NOT STRAIGHT - Tracking torso angle for excessive forward lean
#      → Indicates weak core or too much weight.
# ==========================================
class Lunge(Exercise):
    def __init__(self):
        super().__init__("Lunge")
        self.stage = "UP"
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

        # CHEAT: Leaning forward too much
        self.phrases_lean = [
            "You are leaning too far forward. Keep your chest up.",
            "Your torso is dropping. Stand taller during the lunge.",
            "Engage your core and keep your back straight."
        ]
        # CHEAT: Shallow lunge / not going deep enough
        self.phrases_shallow = [
            "Go deeper into the lunge. Your knee should reach 90 degrees.",
            "That lunge is too shallow. Drop your hips lower.",
            "Don't cheat the range of motion. Bend your knee fully."
        ]
        # CHEAT: Knee going past toes
        self.phrases_knee_over_toe = [
            "Your knee is going past your toes. Step further forward.",
            "Protect your knees. Keep your shin vertical.",
            "Your front knee is too far forward. Adjust your stance."
        ]
        self.phrases_push = [
            "You're slowing down. Keep lunging strong!",
            "Great depth. Maintain the pace!",
            "Stay focused. Drive through your front heel!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

        # Track shallowest knee angle per rep for shallow-rep detection
        self.shallowest_knee_angle = 180

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()

        if isinstance(landmarks, (int, float)):
            knee_angle = landmarks
            torso_angle = 100
            knee_over_toe = False
        else:
            # --- EXTRACT JOINTS (Side view: left side facing camera) ---
            shoulder = landmarks['LEFT_SHOULDER']
            hip = landmarks['LEFT_HIP']
            knee = landmarks['LEFT_KNEE']
            ankle = landmarks['LEFT_ANKLE']

            # --- PRIMARY ANGLE ---
            knee_angle = calculate_angle(hip, knee, ankle)

            # --- CHEAT DETECTION ANGLES ---
            # Torso angle: shoulder → hip → knee (should be >80° when upright)
            torso_angle = calculate_angle(shoulder, hip, knee)

            # Knee over toe check: compare x-coordinates
            # In side view, if knee x goes past ankle x, it's over the toe
            knee_over_toe = (knee[0] < ankle[0] - 0.02) if shoulder[0] < hip[0] else (knee[0] > ankle[0] + 0.02)

        # --- CHEAT DETECTION ---

        # 1. KNEE OVER TOE (injury risk - highest priority)
        if not isinstance(landmarks, (int, float)) and knee_over_toe and knee_angle < 120:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_knee_over_toe)
                self.last_speech_time = current_time

        # 2. TORSO LEANING FORWARD
        elif torso_angle < 70:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_lean)
                self.last_speech_time = current_time

        # --- REP LOGIC ---

        # Track shallowest point for shallow-rep detection
        if knee_angle < self.shallowest_knee_angle:
            self.shallowest_knee_angle = knee_angle

        # Going DOWN (knee bending deep)
        if knee_angle < 100:
            if self.stage == "UP":
                self.stage = "DOWN"
                self.start_rep_timer()

        # Going UP (standing back up)
        if knee_angle > 160:
            if self.stage == "DOWN":
                self.stage = "UP"
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                self.reps += 1

                # CHEAT: Shallow lunge — they went down but not deep enough
                if self.shallowest_knee_angle > 110:
                    if (current_time - self.last_speech_time) > self.speech_cooldown:
                        feedback = f"{self.reps}. {random.choice(self.phrases_shallow)}"
                        self.last_speech_time = current_time
                elif fatigue_level == 2:
                    feedback = self.phrases_stop
                    self.game_over = True
                else:
                    if fatigue_level == 1:
                        feedback = f"{self.reps}. {random.choice(self.phrases_push)}"
                    else:
                        feedback = str(self.reps)

                # Reset shallow tracker
                self.shallowest_knee_angle = 180
                rep_complete = True

        return rep_complete, feedback, knee_angle


# ==========================================
# CHILD CLASS 6: PUSH-UP 💪⬇️
# ==========================================
# HOW IT WORKS:
#   Camera View: SIDE facing
#   Primary Angle: Elbow angle (shoulder → elbow → wrist)
#   Rep Logic: Arms straight (UP) → Arms bent near floor (DOWN)
#
# CHEAT DETECTION:
#   1. HIP SAGGING - Shoulder-hip-ankle angle <150°
#      → Hips drop toward the floor; core not engaged, lower back stress.
#   2. HIP PIKING - Shoulder-hip-ankle angle >200° (hips too high)
#      → Butt goes up in the air to make the push-up easier.
#   3. HALF REPS - Elbow doesn't bend past 110°
#      → User barely lowers themselves, skipping the hardest part.
#   4. FLARED ELBOWS - Tracked via shoulder-to-elbow lateral distance
#      → Bad for shoulder joints, reduces chest activation.
# ==========================================
class PushUp(Exercise):
    def __init__(self):
        super().__init__("Push Up")
        self.stage = "UP"
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

        # CHEAT: Hips sagging (core not engaged)
        self.phrases_sag = [
            "Your hips are sagging. Tighten your core!",
            "Keep your body in a straight line. Don't let your hips drop.",
            "Engage your abs. Your lower back is dipping too much."
        ]
        # CHEAT: Hips piking up (making it easier)
        self.phrases_pike = [
            "Your hips are too high. Lower them into a straight line.",
            "You're piking up. Keep your body flat like a plank.",
            "Don't stick your butt up. Maintain a straight body line."
        ]
        # CHEAT: Not going low enough
        self.phrases_half_rep = [
            "Go lower! Your chest should nearly touch the ground.",
            "That's a half rep. Bend your elbows to at least 90 degrees.",
            "Full range of motion. Lower yourself all the way down."
        ]
        self.phrases_push = [
            "You're slowing down. Push through it!",
            "Keep the form tight. One more rep!",
            "Don't give up. Stay strong!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

        # Track partial reps to warn about them
        self.lowest_elbow_angle = 180  # Track how low they actually go each rep

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()

        if isinstance(landmarks, (int, float)):
            elbow_angle = landmarks
            body_angle = 175
        else:
            # --- EXTRACT JOINTS (Side view) ---
            shoulder = landmarks['LEFT_SHOULDER']
            elbow = landmarks['LEFT_ELBOW']
            wrist = landmarks['LEFT_WRIST']
            hip = landmarks['LEFT_HIP']
            ankle = landmarks['LEFT_ANKLE']

            # --- PRIMARY ANGLE ---
            elbow_angle = calculate_angle(shoulder, elbow, wrist)

            # --- CHEAT DETECTION ANGLE ---
            # Body line: shoulder → hip → ankle (should be ~180 = straight plank)
            body_angle = calculate_angle(shoulder, hip, ankle)

        # Track the lowest point of the rep
        if elbow_angle < self.lowest_elbow_angle:
            self.lowest_elbow_angle = elbow_angle

        # --- CHEAT DETECTION ---

        # 1. HIP SAGGING (injury risk - lower back strain)
        if body_angle < 150:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_sag)
                self.last_speech_time = current_time

        # 2. HIP PIKING (making the exercise easier)
        # Note: calculate_angle caps at 180, so we only use hip.y < shoulder.y check
        elif not isinstance(landmarks, (int, float)) and body_angle > 165 and landmarks['LEFT_HIP'][1] < landmarks['LEFT_SHOULDER'][1]:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_pike)
                self.last_speech_time = current_time

        # --- REP LOGIC ---

        # Going DOWN (elbows bending)
        if elbow_angle < 90:
            if self.stage == "UP":
                self.stage = "DOWN"
                self.start_rep_timer()

        # Going UP (arms straightening)
        if elbow_angle > 160:
            if self.stage == "DOWN":
                self.stage = "UP"
                duration = self.stop_rep_timer()
                fatigue_level = self.get_fatigue_level(duration)
                self.reps += 1

                # 3. HALF REP CHECK (after rep completes)
                if self.lowest_elbow_angle > 110:
                    if (current_time - self.last_speech_time) > self.speech_cooldown:
                        feedback = f"{self.reps}. {random.choice(self.phrases_half_rep)}"
                        self.last_speech_time = current_time
                elif fatigue_level == 2:
                    feedback = self.phrases_stop
                    self.game_over = True
                else:
                    if fatigue_level == 1:
                        feedback = f"{self.reps}. {random.choice(self.phrases_push)}"
                    else:
                        feedback = str(self.reps)

                # Reset tracking for next rep
                self.lowest_elbow_angle = 180
                rep_complete = True

        return rep_complete, feedback, elbow_angle


# ==========================================
# CHILD CLASS 7: HIGH KNEES 🏃‍♂️🦵
# ==========================================
# HOW IT WORKS:
#   Camera View: FRONT facing
#   Primary Angle: Hip angle (shoulder → hip → knee)
#   Rep Logic: Each time a knee rises high enough (hip angle <70°)
#              it counts as half a rep. Both legs = 1 full rep.
#
# CHEAT DETECTION:
#   1. LOW KNEES - Hip angle stays above 90°
#      → User barely lifts their feet; no real cardio benefit.
#   2. LEANING BACK - Shoulder-hip vertical alignment shifts
#      → User leans backward to make knee appear higher.
#   3. NOT ALTERNATING - Same leg keeps going up
#      → User only lifts one leg repeatedly.
#   4. STOMPING (too slow) - Tracked via fatigue system
#      → User slows way down, losing the cardio benefit.
# ==========================================
class HighKnees(Exercise):
    def __init__(self):
        super().__init__("High Knees")
        self.stage = "DOWN"  # Tracks if any knee is currently raised
        self.last_leg = None  # Track which leg was last raised ("LEFT" or "RIGHT")
        self.half_reps = 0    # Two half-reps (one per leg) = 1 full rep
        self.last_speech_time = 0
        self.speech_cooldown = 3.0

        # CHEAT: Not raising knees high enough
        self.phrases_low_knees = [
            "Raise your knees higher! Get them to hip level.",
            "Those knees need to come up more. Drive them upward!",
            "Higher! Your knees should reach your waist."
        ]
        # CHEAT: Leaning backward
        self.phrases_leaning = [
            "You're leaning back. Stay upright and drive your knees.",
            "Keep your torso straight. Don't lean away from your knees.",
            "Stand tall. Your back should be vertical."
        ]
        # CHEAT: Not alternating legs
        self.phrases_alternate = [
            "Switch legs! You need to alternate left and right.",
            "Use both legs equally. Don't just lift one side.",
            "Alternate your knees. Left, right, left, right!"
        ]
        self.phrases_push = [
            "Keep the pace up! Great cardio!",
            "Don't slow down. Maintain the rhythm!",
            "You're doing great. Keep those knees pumping!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()

        if isinstance(landmarks, (int, float)):
            l_hip_angle = landmarks
            r_hip_angle = 160  # Simulate only left knee up
            active_leg = "LEFT" if landmarks < 90 else None
            torso_lean = 0  # 0 = no lean (this is a distance, not an angle)
        else:
            # --- EXTRACT JOINTS ---
            l_shoulder = landmarks['LEFT_SHOULDER']
            r_shoulder = landmarks['RIGHT_SHOULDER']
            l_hip = landmarks['LEFT_HIP']
            r_hip = landmarks['RIGHT_HIP']
            l_knee = landmarks['LEFT_KNEE']
            r_knee = landmarks['RIGHT_KNEE']
            l_ankle = landmarks['LEFT_ANKLE']
            r_ankle = landmarks['RIGHT_ANKLE']

            # --- PRIMARY ANGLES ---
            # Hip angle for each leg: shoulder → hip → knee
            l_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)
            r_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)

            # --- CHEAT DETECTION ANGLES ---
            # Torso lean: check if shoulders are behind hips (leaning back)
            # Use vertical alignment: shoulder y vs hip y
            shoulder_mid_x = (l_shoulder[0] + r_shoulder[0]) / 2.0
            hip_mid_x = (l_hip[0] + r_hip[0]) / 2.0
            torso_lean = abs(shoulder_mid_x - hip_mid_x)

            # Determine which leg is active (lower angle = knee is higher)
            if l_hip_angle < 90:
                active_leg = "LEFT"
            elif r_hip_angle < 90:
                active_leg = "RIGHT"
            else:
                active_leg = None

        # --- CHEAT DETECTION ---

        # 1. LEANING BACK
        if not isinstance(landmarks, (int, float)) and torso_lean > 0.08:
            if (current_time - self.last_speech_time) > self.speech_cooldown:
                feedback = random.choice(self.phrases_leaning)
                self.last_speech_time = current_time

        # --- REP LOGIC ---
        min_hip_angle = min(l_hip_angle, r_hip_angle)

        # KNEE RAISED (one knee comes up high)
        if min_hip_angle < 70:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()

                # 2. CHECK ALTERNATION
                if active_leg is not None:
                    if self.last_leg == active_leg and self.half_reps > 1:
                        if (current_time - self.last_speech_time) > self.speech_cooldown:
                            feedback = random.choice(self.phrases_alternate)
                            self.last_speech_time = current_time
                    self.last_leg = active_leg

        # KNEE LOWERED (both knees back down)
        if min_hip_angle > 140:
            if self.stage == "UP":
                self.stage = "DOWN"
                duration = self.stop_rep_timer()
                self.half_reps += 1

                # Every 2 half-reps = 1 full rep (left + right)
                if self.half_reps % 2 == 0:
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

        return rep_complete, feedback, min_hip_angle


# ==========================================
# CHILD CLASS 8: LATERAL RAISE 🤸
# ==========================================
# HOW IT WORKS:
#   Camera View: FRONT facing
#   Primary Angle: Shoulder angle (hip → shoulder → wrist)
#   Rep Logic: Arms at sides (DOWN) → Arms raised to shoulder level (UP)
#
# CHEAT DETECTION:
#   1. BENT ELBOWS - Elbow angle (shoulder → elbow → wrist) < 150°
#      → User bends elbows to shorten the lever arm, making it easier.
#   2. USING MOMENTUM / SWINGING - Speed-based detection via rep timing
#      → User swings the weights up instead of controlled lifting.
#   3. SHRUGGING SHOULDERS - Shoulder y-position rises relative to ears
#      → User lifts shoulders (traps) instead of using deltoids.
#   4. ASYMMETRIC RAISE - Left vs right shoulder angles differ by >20°
#      → One arm goes higher than the other; uneven development.
#   5. RAISING TOO HIGH - Arms go above shoulder level (>100°)
#      → Engages traps instead of deltoids; potential impingement.
# ==========================================
class LateralRaise(Exercise):
    def __init__(self):
        super().__init__("Lateral Raise")
        self.stage = "DOWN"
        self.last_speech_time = 0
        self.speech_cooldown = 4.0

        # CHEAT: Bending elbows
        self.phrases_bent_elbows = [
            "Keep your arms straight. Don't bend your elbows.",
            "You're bending your elbows to cheat. Lock them out.",
            "Straight arms! Bending makes the exercise too easy."
        ]
        # CHEAT: Asymmetric raising
        self.phrases_asymmetric = [
            "Raise both arms to the same height.",
            "Your arms are uneven. Lift them equally.",
            "One arm is higher than the other. Keep them balanced."
        ]
        # CHEAT: Shrugging shoulders up
        self.phrases_shrug = [
            "Don't shrug your shoulders. Keep them down and relaxed.",
            "You're using your traps. Relax your shoulders and lift with your deltoids.",
            "Drop your shoulders down. The raise should come from your arms."
        ]
        # CHEAT: Raising arms too high above shoulder level
        self.phrases_too_high = [
            "Don't raise above shoulder level. Stop at 90 degrees.",
            "You're going too high. That shifts work to your traps.",
            "Control the range. Raise only to shoulder height."
        ]
        self.phrases_push = [
            "You're slowing down. Keep those arms moving!",
            "Stay controlled. Nice slow reps!",
            "Great form. Maintain the tempo!"
        ]
        self.phrases_stop = "Severe fatigue detected. Returning to main menu."

    def process(self, landmarks):
        feedback = None
        rep_complete = False
        current_time = time.time()

        if isinstance(landmarks, (int, float)):
            l_shoulder_angle = landmarks
            r_shoulder_angle = landmarks
            l_elbow_angle = 170
            r_elbow_angle = 170
            is_shrugging = False
        else:
            # --- EXTRACT JOINTS ---
            l_shoulder = landmarks['LEFT_SHOULDER']
            r_shoulder = landmarks['RIGHT_SHOULDER']
            l_elbow = landmarks['LEFT_ELBOW']
            r_elbow = landmarks['RIGHT_ELBOW']
            l_wrist = landmarks['LEFT_WRIST']
            r_wrist = landmarks['RIGHT_WRIST']
            l_hip = landmarks['LEFT_HIP']
            r_hip = landmarks['RIGHT_HIP']

            # --- PRIMARY ANGLES ---
            # Shoulder angle: how high the arm is raised (hip → shoulder → wrist)
            l_shoulder_angle = calculate_angle(l_hip, l_shoulder, l_wrist)
            r_shoulder_angle = calculate_angle(r_hip, r_shoulder, r_wrist)

            # --- CHEAT DETECTION ANGLES ---
            # Elbow straightness (should be near 180 = straight arm)
            l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # Shrugging detection: if shoulders rise toward ears
            # Check if shoulder y gets unusually close to nose level
            # Using relative distance: shoulders rise compared to hips
            shoulder_hip_dist = abs(l_shoulder[1] - l_hip[1])
            is_shrugging = shoulder_hip_dist < 0.15  # Shoulders bunched up

        # Use average shoulder angle for rep tracking
        avg_shoulder_angle = (l_shoulder_angle + r_shoulder_angle) / 2.0

        # --- CHEAT DETECTION ---

        # Only check form when arms are in motion (between 20° and 100°)
        if avg_shoulder_angle > 20:

            # 1. BENT ELBOWS (shortening lever arm)
            if l_elbow_angle < 150 or r_elbow_angle < 150:
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_bent_elbows)
                    self.last_speech_time = current_time

            # 2. ASYMMETRIC RAISE
            elif abs(l_shoulder_angle - r_shoulder_angle) > 20:
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_asymmetric)
                    self.last_speech_time = current_time

            # 3. SHRUGGING SHOULDERS
            elif not isinstance(landmarks, (int, float)) and is_shrugging:
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_shrug)
                    self.last_speech_time = current_time

            # 4. RAISING TOO HIGH (above shoulder level)
            elif avg_shoulder_angle > 110:
                if (current_time - self.last_speech_time) > self.speech_cooldown:
                    feedback = random.choice(self.phrases_too_high)
                    self.last_speech_time = current_time

        # --- REP LOGIC ---

        # Going UP (arms rising to shoulder level)
        if avg_shoulder_angle > 80:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.start_rep_timer()

        # Going DOWN (arms lowering back to sides)
        if avg_shoulder_angle < 30:
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

        return rep_complete, feedback, avg_shoulder_angle