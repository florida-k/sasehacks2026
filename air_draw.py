import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

canvas = None
prev_x, prev_y = None, None

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if canvas is None:
            canvas = np.zeros_like(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        drawing = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                tip = hand_landmarks.landmark[8]
                joint = hand_landmarks.landmark[6]

                x = int(tip.x * w)
                y = int(tip.y * h)

                # check if finger is raised
                if tip.y < joint.y:
                    drawing = True
                    cv2.circle(frame, (x, y), 10, (0,255,0), -1)

                    if prev_x is None:
                        prev_x, prev_y = x, y

                    cv2.line(canvas, (prev_x, prev_y), (x, y), (255,0,0), 5)

                    prev_x, prev_y = x, y

                else:
                    prev_x, prev_y = None, None

        else:
            prev_x, prev_y = None, None

        frame = cv2.add(frame, canvas)

        cv2.putText(frame,
                    "Index finger up = draw | Close hand = stop | C = clear | Q = quit",
                    (10,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255,255,255),
                    2)

        cv2.imshow("Air Drawing", frame)

        key = cv2.waitKey(1)

        if key == ord("q"):
            break
        if key == ord("c"):
            canvas = np.zeros_like(frame)

cap.release()
cv2.destroyAllWindows()