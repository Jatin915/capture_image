import face_recognition
import numpy as np
import cv2

def compare_faces(img1_path, img2_path, tolerance=0.6):
    try:
        img1 = face_recognition.load_image_file(img1_path)
        img2 = face_recognition.load_image_file(img2_path)

        enc1 = face_recognition.face_encodings(img1)
        enc2 = face_recognition.face_encodings(img2)

        if len(enc1) == 0 or len(enc2) == 0:
            return {"match": False, "reason": "No face detected"}

        result = face_recognition.compare_faces([enc1[0]], enc2[0], tolerance)
        distance = face_recognition.face_distance([enc1[0]], enc2[0])[0]

        return {
            "match": result[0],
            "distance": float(distance)
        }

    except Exception as e:
        return {"error": str(e)}
