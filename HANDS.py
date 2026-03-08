import re
import numpy as np
import time
import subprocess
import psutil 

from pynput.keyboard import Controller
keyboard = Controller()

script_started=False
name_script = "hands_3d_final.py"

# objectreadfile = "PIEZA6.obj"

isfullscreen = "NO"
makefullscreen = False
if isfullscreen == "SI":
    makefullscreen = True

isoptimized = "SI"
makeoptimize = False
if isoptimized == "SI":
    makeoptimize = True

# Declaración del total de áreas a mostrar
totalpush = int(11)
touchcaps = []

# Definición de áreas de gestos
touchcaps.append({"id": 1, "cap1": (7, 14), "cap2": (137, 110),     "com": ["a"], "last": 0, "detected": False})  # 1
touchcaps.append({"id": 2, "cap1": (178, 14), "cap2": (306, 110),   "com": ["b"], "last": 0, "detected": False})  # 2
touchcaps.append({"id": 3, "cap1": (344, 14), "cap2": (467, 110),   "com": ["c"], "last": 0, "detected": False})  # 3
touchcaps.append({"id": 4, "cap1": (507, 15), "cap2": (630, 102),   "com": ["d"], "last": 0, "detected": False})  # 4
touchcaps.append({"id": 5, "cap1": (8, 135), "cap2": (139, 234),    "com": ["e"], "last": 0, "detected": False})  # 5
touchcaps.append({"id": 6, "cap1": (244, 154), "cap2": (409, 230),  "com": ["f"], "last": 0, "detected": False})  # 6
touchcaps.append({"id": 7, "cap1": (507, 133), "cap2": (631, 209),  "com": ["g"], "last": 0, "detected": False})  # 7
touchcaps.append({"id": 8, "cap1": (10, 258), "cap2": (140, 358),   "com": ["h"], "last": 0, "detected": False})  # 8
touchcaps.append({"id": 9, "cap1": (182, 258), "cap2": (307, 358),  "com": ["i"], "last": 0, "detected": False})  # 9
touchcaps.append({"id": 10, "cap1": (348, 258), "cap2": (467, 358), "com": ["j"], "last": 0, "detected": False})  # 10
touchcaps.append({"id": 11, "cap1": (507, 231), "cap2": (633, 358), "com": ["k"], "last": 0, "detected": False})  # 11



print("Ejecutando...")
import mediapipe as mp
import cv2
import numpy as np
from math import sqrt
import uuid
import os

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#en estas lineas es donde se indica el indice de la camara
#es decir que camara se usara
if makeoptimize:
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)

# =====Medidas de la ventana principal======
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
# =========================================
counter = 0
lastgestureX = 0
lastgestureY = 0
lastgestureZ = 0
moveDelta = 30
lastmoveX = 0
lastmoveY = 0
lastmoveZ = 0
waitframe = True
moveX = 0
moveY = 0
moveZ = 0
newZ = True
refZ = 0
absZ = 0
initialpose = True
zoomcounter = 0

#funcion para calcular la disyancia entre dos puntos
#esta funcion esta en desuso ya que ya no se necesita calcualr la distancia
#esto debido a que ya no se abre aqui modelos 3d
#def calc_distance(p1, p2):
 #   return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

# Agrega una variable para rastrear si la mano está dentro de una región
hand_inside_region = False

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():

      
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frameWidth = image.shape[1]
        frameHeight = image.shape[0]

        image = cv2.flip(image, 1)

        image.flags.writeable = False

        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        pos = (0, 0)
          #se encarga de dibujar un rectángulo relleno en la imagen de video capturada por la cámara
        cv2.rectangle(image, pos, (frameWidth, frameHeight), (0, 0, 0), -1)

        # # Nueva lista para rastrear las manos que están dentro de las regiones
        hands_inside_regions = [False] * len(touchcaps)

        totalHands = 0
 ##################################################################

       
#####################################################################


        if results.multi_handedness:
            totalHands = len(results.multi_handedness)
            if(totalHands == 2):
                if(results.multi_handedness[0].classification[0].label == results.multi_handedness[1].classification[0].label):
                    totalHands = 1

        if results.multi_hand_landmarks:
            if initialpose:
                initialpose = False
            if(totalHands == 1):
                for num, hand in enumerate(results.multi_hand_landmarks):
                    indexTip = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    indexTipXY = mp_drawing._normalized_to_pixel_coordinates(indexTip.x, indexTip.y, frameWidth, frameHeight)

                    thumbTip = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.THUMB_TIP]
                    thumbTipXY = mp_drawing._normalized_to_pixel_coordinates(thumbTip.x, thumbTip.y, frameWidth, frameHeight)

                    if indexTipXY and thumbTipXY is not None:
                        indexXY = (indexTipXY[0], indexTipXY[1])
                        thumbXY = (thumbTipXY[0], thumbTipXY[1])

                        for i, r in enumerate(touchcaps):
                            if r["cap1"][0] < indexXY[0] < r["cap2"][0] and r["cap1"][1] < indexXY[1] < r["cap2"][1]:
                                if not r["detected"]:
                                    r["detected"] = True
                                    lastcom = r["last"]
                                    command = r["com"][lastcom]
                                    r["last"] = r["last"] + 1
                                    if r["last"] >= len(r["com"]):
                                        r["last"] = 0
                                    print(command)
                                    keyboard.press(command)
                                    time.sleep(0.1)
                                    keyboard.release(command)

                                # Marca la mano actual como dentro de la región correspondiente
                                hands_inside_regions[i] = True

                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2))

            elif(totalHands == 2):

                handX = [0, 0]
                handY = [0, 0]
                isHands = [False, False] 

                for num, hand in enumerate(results.multi_hand_landmarks):

                    indexTip = results.multi_hand_landmarks[num].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    indexTipXY = mp_drawing._normalized_to_pixel_coordinates(indexTip.x, indexTip.y, frameWidth, frameHeight)

                    thumbTip = results.multi_hand_landmarks[num].landmark[mp_hands.HandLandmark.THUMB_TIP]
                    thumbTipXY = mp_drawing._normalized_to_pixel_coordinates(thumbTip.x, thumbTip.y, frameWidth, frameHeight)

                    if indexTipXY and thumbTipXY is not None:
                        indexXY = (indexTipXY[0], indexTipXY[1])
                        thumbXY = (thumbTipXY[0], thumbTipXY[1])
                         #Se modificó el código que verifica si una mano está dentro 
                         # de una región para marcar la mano actual como dentro de la 
                         # región correspondiente y actualizar la lista hands_inside_regions.
                        for i, r in enumerate(touchcaps):
                            if r["cap1"][0] < indexXY[0] < r["cap2"][0] and r["cap1"][1] < indexXY[1] < r["cap2"][1]:
                                if not r["detected"]:
                                    r["detected"] = True
                                    lastcom = r["last"]
                                    command = r["com"][lastcom]
                                    r["last"] = r["last"] + 1
                                    if r["last"] >= len(r["com"]):
                                        r["last"] = 0
                                    print(command)
                                    keyboard.press(command)
                                    time.sleep(0.1)
                                    keyboard.release(command)

                                # Marca la mano actual como dentro de la región correspondiente
                                hands_inside_regions[i] = True

                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                            mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
                        )

        else:
            if not initialpose:
                initialpose = True
                print("Posición inicial (MACV)")

        #Verifica si alguna mano está dentro de una región
        hand_inside_region = any(hands_inside_regions)

        # Si hand_inside_region es False, significa que ninguna mano está dentro de una región,
        # por lo que se resetea la variable "detected" de todas las regiones
        if not hand_inside_region:
            for r in touchcaps:
                r["detected"] = False

        # Dibuja las figuras después de verificar si la mano está dentro de una región
        for r in touchcaps:
            #para definir un color del contorno de cada figura
            cv2.rectangle(image, r["cap1"], r["cap2"], (255, 255, 255), 1)

        if not makefullscreen:
            cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

cap.release()
cv2.destroyAllWindows()
