class RepCounter:
    def __init__(self):
        self.reps = 0
        self.stage = "UP"  # User starts in standing position

    def process_angle(self, knee_angle):
        """
        Input: knee_angle (number)
        Output: Current Rep Count (number)
        """
        # 1. Detect Going Down (Squatting)
        # If angle is small (< 90), it means knee is bent
        if knee_angle < 90:
            if self.stage == "UP":
                self.stage = "DOWN"
                print(" -> Logic: User is DOWN")

        # 2. Detect Coming Up (Standing)
        # If angle is large (> 160), leg is straight
        if knee_angle > 160:
            if self.stage == "DOWN":
                self.stage = "UP"
                self.reps += 1
                print(f" -> Logic: REP COMPLETE! Total: {self.reps}")
                return True # Signal that a new rep just happened
        
        return False