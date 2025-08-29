from flask import Flask, request, jsonify
import os
import cv2
import face_recognition
from datetime import datetime

app = Flask(__name__)

# Uploads folder setup
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy students data (with photo paths stored locally)
students = [
    {"id": 1, "name": "Amit Kumar", "photo": "students/amit.jpg"},
    {"id": 2, "name": "Neha Sharma", "photo": "students/neha.jpg"},
    {"id": 3, "name": "Ravi Verma", "photo": "students/ravi.jpg"},
]

attendance = {}

def mark_attendance(student_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance[student_id] = {"time": now, "status": "Present"}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save file in uploads
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Load uploaded image
    uploaded_img = face_recognition.load_image_file(file_path)
    uploaded_encodings = face_recognition.face_encodings(uploaded_img)

    if not uploaded_encodings:
        return jsonify({"error": "No face detected"}), 400

    uploaded_encoding = uploaded_encodings[0]

    # Compare with each student
    for student in students:
        known_img = face_recognition.load_image_file(student['photo'])
        known_encodings = face_recognition.face_encodings(known_img)

        if not known_encodings:
            continue

        match = face_recognition.compare_faces([known_encodings[0]], uploaded_encoding)

        if match[0]:  # Face matched
            mark_attendance(student['id'])
            return jsonify({
                "message": f"Attendance marked for {student['name']}",
                "student": student,
                "attendance": attendance[student['id']]
            })

    return jsonify({"message": "No match found"}), 404


@app.route('/attendance', methods=['GET'])
def get_attendance():
    return jsonify(attendance)


if __name__ == '__main__':
    app.run(debug=True)
