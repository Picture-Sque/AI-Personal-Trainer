import numpy as np

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points (A, B, C).
    
    Arguments:
    a -- Point A [x, y] (e.g., Shoulder)
    b -- Point B [x, y] (The Joint, e.g., Elbow)
    c -- Point C [x, y] (e.g., Wrist)
    
    Returns:
    angle -- The angle in degrees (0 to 180)
    """
    # Convert inputs to NumPy arrays for easy math
    a = np.array(a) # Start Point
    b = np.array(b) # Mid Point (The Joint)
    c = np.array(c) # End Point
    
    # math.atan2(y, x) calculates the angle of a vector
    # We create two vectors: BA (Joint to Start) and BC (Joint to End)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    
    # Convert radians to degrees
    angle = np.abs(radians * 180.0 / np.pi)
    
    # Ensure the angle is always within 0-180 range
    # (Because joints don't usually bend 360 degrees)
    if angle > 180.0:
        angle = 360 - angle
        
    return angle