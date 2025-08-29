import face_recognition
import os

KNOWN_FACES_DIR = "./known_faces/"

def load_known_faces():
    known_encodings = []
    known_names = []

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:  # only if face found
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])

    return known_encodings, known_names


def recognize_face(image_path):
    known_encodings, known_names = load_known_faces()

    unknown_image = face_recognition.load_image_file(image_path)
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if not unknown_encodings:
        return {"success": False, "message": "No face detected"}

    for unknown_encoding in unknown_encodings:
        results = face_recognition.compare_faces(known_encodings, unknown_encoding)
        if True in results:
            match_index = results.index(True)
            return {"success": True, "name": known_names[match_index]}

    return {"success": False, "message": "Face not recognized"}
