from utils import calculate_angle

# Test Case 1: A perfect right angle (90 degrees)
# Imagine: Shoulder at (0,1), Elbow at (0,0), Wrist at (1,0)
shoulder = [0, 1]
elbow = [0, 0]
wrist = [1, 0]

angle = calculate_angle(shoulder, elbow, wrist)
print(f"Test 1 (Should be 90.0): {angle}")

# Test Case 2: A straight arm (180 degrees)
shoulder = [0, 1]
elbow = [0, 0]
wrist = [0, -1]

angle = calculate_angle(shoulder, elbow, wrist)
print(f"Test 2 (Should be 180.0): {angle}")