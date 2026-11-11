import cv2
import mediapipe as mp

# Initialize mediapipe solutions
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Video capture from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError('Webcam could not be opened')

with (
    mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose,
    mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands,
):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert the BGR image to RGB.
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        # Process pose and hands
        pose_results = pose.process(rgb)
        hands_results = hands.process(rgb)
        rgb.flags.writeable = True
        # Convert back to BGR for OpenCV
        annotated = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(
                annotated,
                pose_results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(255,0,0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2)
            )
        # Draw hand landmarks
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255,255,0), thickness=2, circle_radius=2)
                )
        cv2.imshow('Pose and Hands', annotated)
        if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
            break

cap.release()
cv2.destroyAllWindows()
