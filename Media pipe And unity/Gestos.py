"""Script para detección de manos y envío de datos a Unity y Arduino."""
import socket  # Librería estándar primero
import cv2     # Librerías de terceros después
from cvzone.HandTrackingModule import HandDetector

import controller as cnt  # Tus propios archivos al final

# 1. Configuración del Socket UDP (Puente con Unity)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052) 

# 2. Configuración de Cámara y Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)
video = cv2.VideoCapture(0)
video.set(3, 640) # Optimizamos para tu ThinkPad
video.set(4, 480)

while True:
    ret, frame = video.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    hands, img = detector.findHands(frame)
    
    if hands:
        # Obtenemos los 21 puntos (Landmarks)
        lmList = hands[0]['lmList'] 
        fingerUp = detector.fingersUp(hands[0])

        # 3. Preparar datos para Unity
        # Convertimos la lista de puntos a una cadena simple
        dataToSend = []
        for lm in lmList:
            # Mandamos X, Y, Z de cada punto. Invertimos Y para Unity.
            dataToSend.extend([lm[0], 480 - lm[1], lm[2]]) 
        
        # Enviamos los datos por el puerto 5052
        sock.sendto(str(dataToSend).encode(), serverAddressPort)

        # 4. Control de Arduino (Tu lógica original)
        cnt.led(fingerUp)
        
        # (Opcional) Dibujar el conteo en pantalla para referencia
        totalFingers = fingerUp.count(1)
        cv2.putText(frame, f'Fingers: {totalFingers}', (20, 460),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == ord("k"):
        break

video.release()
cv2.destroyAllWindows()