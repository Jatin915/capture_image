# liveness.py
import cv2
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh

# Eye landmark indices for Mediapipe (left eye example)
LEFT_EYE = [33, 160, 158, 133, 153, 144]  # [p1, p2, p3, p4, p5, p6]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]  # [p1, p2, p3, p4, p5, p6]

# EAR threshold for blink
EAR_THRESHOLD = 0.21

def eye_aspect_ratio(landmarks, eye_indices):
    """Compute EAR for one eye using Mediapipe landmarks."""
    a = math.hypot(
        landmarks[eye_indices[1]][0] - landmarks[eye_indices[5]][0],
        landmarks[eye_indices[1]][1] - landmarks[eye_indices[5]][1]
    )
    b = math.hypot(
        landmarks[eye_indices[2]][0] - landmarks[eye_indices[4]][0],
        landmarks[eye_indices[2]][1] - landmarks[eye_indices[4]][1]
    )
    c = math.hypot(
        landmarks[eye_indices[0]][0] - landmarks[eye_indices[3]][0],
        landmarks[eye_indices[0]][1] - landmarks[eye_indices[3]][1]
    )
    ear = (a + b) / (2.0 * c) if c != 0 else 0
    return ear

def check_liveness():
    cap = cv2.VideoCapture(0)
    blink_counter = 0
    eyes_closed = False  # Track eye state to count one blink at a time

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Extract landmarks into list of tuples
                    landmarks = [(lm.x, lm.y) for lm in face_landmarks.landmark]

                    left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
                    right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
                    avg_ear = (left_ear + right_ear) / 2.0

                    # Blink detection logic
                    if avg_ear < EAR_THRESHOLD:
                        if not eyes_closed:
                            blink_counter += 1
                            eyes_closed = True  # mark eyes closed
                    else:
                        eyes_closed = False  # eyes are open again

                    # Display
                    cv2.putText(frame, f"Blinks: {blink_counter}", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # Stop after 2 blinks
                    if blink_counter >= 2:
                        cap.release()
                        cv2.destroyAllWindows()
                        return True

            cv2.imshow("Liveness Check", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return False
