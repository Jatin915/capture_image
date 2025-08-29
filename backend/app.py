# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, json
from datetime import datetime
import numpy as np
import face_recognition
from Face_Recognition.backend.face_utils import (
    load_json, save_json, compute_encoding_from_path,
    compute_encodings_from_uploaded_file, encoding_to_list, list_to_encoding
)

app = Flask(__name__)
CORS(app)

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
STUDENTS_JSON = os.path.join(DATA_DIR, "students.json")
ENCODINGS_JSON = os.path.join(DATA_DIR, "encodings.json")
ATTENDANCE_JSON = os.path.join(DATA_DIR, "attendance.json")
STUDENTS_FOLDER = os.path.join(ROOT, "students")
UPLOADS_FOLDER = os.path.join(ROOT, "uploads")

os.makedirs(STUDENTS_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure files exist
for p, default in [(ENCODINGS_JSON, {}), (ATTENDANCE_JSON, {})]:
    if not os.path.exists(p):
        save_json(p, default)

@app.route("/api/students", methods=["GET"])
def get_students():
    students = load_json(STUDENTS_JSON)
    return jsonify(students)

@app.route("/api/enroll", methods=["POST"])
def enroll():
    """
    Enroll a single student by sending form-data:
      - student_id (int)
      - image (file)
    This will save student's reference image (students/<id>.jpg) and compute embedding stored in encodings.json
    """
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"error": "student_id required"}), 400

    if "image" not in request.files:
        return jsonify({"error": "image file required"}), 400

    img = request.files["image"]
    filename = f"student_{student_id}_{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(STUDENTS_FOLDER, filename)
    img.save(save_path)

    enc = compute_encoding_from_path(save_path)
    if enc is None:
        os.remove(save_path)
        return jsonify({"error": "No face detected in provided image"}), 400

    encodings = load_json(ENCODINGS_JSON)
    encodings[str(student_id)] = encoding_to_list(enc)
    save_json(ENCODINGS_JSON, encodings)

    # Optionally also add / update students.json entry (user can maintain students.json manually)
    students = load_json(STUDENTS_JSON) or []
    found = False
    for s in students:
        if str(s.get("id")) == str(student_id):
            s["photo"] = os.path.join("students", filename)
            found = True
            break
    if not found:
        # Add minimal record
        students.append({"id": int(student_id), "name": f"Student {student_id}", "enrollment": "", "photo": os.path.join("students", filename)})
    save_json(STUDENTS_JSON, students)

    return jsonify({"ok": True, "student_id": student_id})

@app.route("/api/upload", methods=["POST"])
def upload_and_match():
    """
    Receive form-data with 'image' file (a capture). Save it to uploads/
    Compute embeddings for all faces in the uploaded image, compare to enrolled encodings.
    Mark attendance in attendance.json for matched students (per-date).
    Returns matched student ids / names and distances.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file in request"}), 400

    file = request.files["image"]
    fname = f"{uuid.uuid4().hex}.jpg"
    saved_path = os.path.join(UPLOADS_FOLDER, fname)
    file.save(saved_path)

    # get encodings from uploaded (could be multiple faces)
    try:
        uploaded_encs = compute_encodings_from_uploaded_file(saved_path)
    except Exception as e:
        return jsonify({"error": "Error processing uploaded image", "detail": str(e)}), 500

    if not uploaded_encs:
        return jsonify({"error": "No faces detected in uploaded image"}), 400

    # load enrolled encodings
    encodings_map = load_json(ENCODINGS_JSON)
    # convert to numpy arrays
    enrolled = {sid: np.array(vec) for sid, vec in encodings_map.items()}

    # comparisons
    matched = {}  # sid -> best distance
    for u_enc in uploaded_encs:
        for sid, k_enc in enrolled.items():
            dist = np.linalg.norm(k_enc - u_enc)
            # threshold (tune if needed)
            if dist <= 0.6:
                # store smallest distance if multiple faces
                prev = matched.get(sid)
                if prev is None or dist < prev:
                    matched[sid] = float(dist)

    # mark attendance for matched
    attendance = load_json(ATTENDANCE_JSON)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    attendance.setdefault(today, [])

    # load students list for names
    students = load_json(STUDENTS_JSON) or []

    result_matches = []
    for sid, dist in matched.items():
        sid_int = int(sid)
        if sid_int not in attendance[today]:
            attendance[today].append(sid_int)
        # find name
        name = next((s.get("name") for s in students if int(s.get("id")) == sid_int), f"Student {sid}")
        result_matches.append({"id": sid_int, "name": name, "distance": dist})

    save_json(ATTENDANCE_JSON, attendance)

    if result_matches:
        return jsonify({"matches": result_matches, "upload": fname})
    else:
        return jsonify({"matches": [], "upload": fname, "message": "No match found"}), 404

@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    attendance = load_json(ATTENDANCE_JSON)
    return jsonify(attendance)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
