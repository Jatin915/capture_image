# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from backend.face_utils import recognize_face
from backend.liveness import check_liveness  # the blink-based liveness module

app = FastAPI()

# CORS settings to allow your frontend (Vite/React)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/attendance")
async def mark_attendance(file: UploadFile = File(...)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Liveness check first
    is_live = check_liveness()
    if not is_live:
        return {"success": False, "message": "Liveness check failed. Please blink to verify."}

    # Face recognition
    recognized_name = recognize_face(file_path)
    if recognized_name:
        # Here you can implement storing attendance in DB or JSON
        return {"success": True, "message": f"Attendance marked for {recognized_name}"}
    else:
        return {"success": False, "message": "Face not recognized."}
