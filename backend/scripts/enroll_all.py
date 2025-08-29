# backend/scripts/enroll_all.py
import os, json
from Face_Recognition.backend.face_utils import compute_encoding_from_path, encoding_to_list, save_json, load_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
STUDENTS_JSON = os.path.join(DATA_DIR, "students.json")
ENCODINGS_JSON = os.path.join(DATA_DIR, "encodings.json")

students = load_json(STUDENTS_JSON) or []
enc = load_json(ENCODINGS_JSON) or {}

for s in students:
    sid = str(s.get("id"))
    photo = s.get("photo")
    if not photo:
        continue
    path = os.path.join(ROOT, photo)
    if not os.path.exists(path):
        print("Missing photo for", sid, path)
        continue
    e = compute_encoding_from_path(path)
    if e is None:
        print("No face detected for", sid)
        continue
    enc[sid] = encoding_to_list(e)
    print("Enrolled", sid)
save_json(ENCODINGS_JSON, enc)
print("Done. Encodings saved:", ENCODINGS_JSON)
