# vr_hand_tracker.py
import cv2
import mediapipe as mp
import numpy as np
from virtual_keyboard import draw_keyboard, detect_key_press, keyboard_layout
from utils import initialize_kalman

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def get_vr_camera_feed():
    """
    Placeholder for VR headset camera feed.
    Replace with VR SDK-specific code (e.g., Oculus SDK for Quest 2).
    """
    # For testing, use a standard webcam (index 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera. Ensure VR headset or webcam is connected.")
        exit(1)
    return cap

def render_to_vr(image):
    """
    Placeholder for rendering to VR headset.
    Replace with VR SDK rendering (e.g., OpenVR IVRCompositor or Oculus TextureSwapChain).
    """
    # For testing, use OpenCV display
    cv2.imshow('VR Hand Tracking', image)

def main():
    """Main loop for VR hand tracking with MediaPipe."""
    cap = get_vr_camera_feed()
    kfs = [initialize_kalman() for _ in range(5)]  # Kalman filters for fingertips

    with mp_hands.Hands(
        model_complexity=0,  # Low complexity for real-time VR performance
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to read VR camera frame.")
                break

            # Process frame with MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw virtual keyboard
            image = draw_keyboard(image)

            # Process hand landmarks with optional Kalman smoothing
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Apply Kalman filter to fingertip landmarks (optional enhancement)
                    for i, kf in enumerate(kfs):
                        tip_idx = mp_hands.HandLandmark.INDEX_FINGER_TIP + i * 4
                        z = np.array([
                            hand_landmarks.landmark[tip_idx].x,
                            hand_landmarks.landmark[tip_idx].y,
                            hand_landmarks.landmark[tip_idx].z
                        ])
                        kf.predict()
                        kf.update(z)
                        hand_landmarks.landmark[tip_idx].x, \
                        hand_landmarks.landmark[tip_idx].y, \
                        hand_landmarks.landmark[tip_idx].z = kf.x

                    # Draw landmarks
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

                    # Detect key presses
                    pressed_keys = detect_key_press(hand_landmarks, image, keyboard_layout)
                    if pressed_keys:
                        print(f"Pressed: {pressed_keys}")

            # Render to VR (or display for testing)
            render_to_vr(image)

            # Exit on 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
