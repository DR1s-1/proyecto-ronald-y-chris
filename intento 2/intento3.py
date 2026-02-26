import cv2
import mediapipe as mp
import time
import numpy as np
from pyfirmata import Arduino

# Conexión con Arduino Mega (ajusta el puerto COM)
board = Arduino('COM3')
servo = board.get_pin('d:6:s')  # Servo en pin digital 9
time.sleep(1)

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

# Umbrales de distancia
CLOSE_T = 55   # dedos juntos -> servo a 0°
OPEN_T = 75   # dedos separados -> servo a 180°
last_cmd = None
d_buffer = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm = handLms.landmark
            h, w, _ = frame.shape

            # Coordenadas pulgar e índice
            x1, y1 = int(lm[4].x * w), int(lm[4].y * h)   # Pulgar
            x2, y2 = int(lm[8].x * w), int(lm[8].y * h)   # Índice

            # Dibujar puntos y línea
            cv2.circle(frame, (x1, y1), 8, (0, 0, 255), -1)
            cv2.circle(frame, (x2, y2), 8, (0, 255, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Calcular distancia
            dist = np.hypot(x2 - x1, y2 - y1)

            # Suavizado
            d_buffer.append(dist)
            if len(d_buffer) > 5:
                d_buffer.pop(0)
            d_avg = np.mean(d_buffer)

            # Control del servo
            if d_avg < CLOSE_T and last_cmd != 200:
                servo.write(200)
                last_cmd = 200
            elif d_avg > OPEN_T and last_cmd != 100:
                servo.write(100)
                last_cmd = 100

            # Mostrar distancia
            cv2.putText(frame, f"Dist: {int(d_avg)}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Servo Control - Pulgar/Indice", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
board.exit()
