import cv2
import mediapipe as mp
import numpy as np

class VisionEngine:
    def __init__(self):
        # 1. SETUP MEDIAPIPE 
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )

    def process_frame(self, frame):
        """
        Takes a raw camera frame, finds the skeleton, 
        and returns a clean Dictionary of coordinates.
        """
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        results = self.pose.process(image)
      
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        landmark_dict = {}

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            def get_point(landmark_name):
                return [
                    landmarks[landmark_name.value].x,
                    landmarks[landmark_name.value].y
                ]

            # --- PACKAGING DATA FOR THE BRAIN ---
            try:
                landmark_dict = {
                    'LEFT_SHOULDER': get_point(self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                    'LEFT_ELBOW':    get_point(self.mp_pose.PoseLandmark.LEFT_ELBOW),
                    'LEFT_WRIST':    get_point(self.mp_pose.PoseLandmark.LEFT_WRIST),
                    'LEFT_HIP':      get_point(self.mp_pose.PoseLandmark.LEFT_HIP),
                    'LEFT_KNEE':     get_point(self.mp_pose.PoseLandmark.LEFT_KNEE),
                    'LEFT_ANKLE':    get_point(self.mp_pose.PoseLandmark.LEFT_ANKLE),
                    
                    # RIGHT SIDE ADDED FOR FULL BODY TRACKING (Jumping Jacks)
                    'RIGHT_SHOULDER': get_point(self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                    'RIGHT_ELBOW':    get_point(self.mp_pose.PoseLandmark.RIGHT_ELBOW),
                    'RIGHT_WRIST':    get_point(self.mp_pose.PoseLandmark.RIGHT_WRIST),
                    'RIGHT_HIP':      get_point(self.mp_pose.PoseLandmark.RIGHT_HIP),
                    'RIGHT_KNEE':     get_point(self.mp_pose.PoseLandmark.RIGHT_KNEE),
                    'RIGHT_ANKLE':    get_point(self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                }
            except:
                pass 
            
            self.mp_drawing.draw_landmarks(
                image, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
        return image, landmark_dict