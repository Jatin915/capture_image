from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import base64
import os
import uuid
from face_utils import recognize_face

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to ["http://localhost:5173"] if using Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Face Recognition API Running!"}


@app.post("/attendance")
async def mark_attendance(request: Request):
    data = await request.json()
    student_id = data.get("studentId")
    image_data = data.get("image")  # base64 string

    if not image_data:
        return {"success": False, "message": "No image received"}

    # Remove base64 prefix (data:image/jpeg;base64,...)
    if image_data.startswith("data:image"):
        image_data = image_data.split(",")[1]

    # Decode and save temporary image
    img_bytes = base64.b64decode(image_data)
    file_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(img_bytes)

    # Run recognition
    result = recognize_face(file_path)

    # Clean up
    os.remove(file_path)

    if result.get("success"):
        return {
            "success": True,
            "message": f"Attendance marked for {result['name']}",
            "studentId": student_id
        }
    else:
        return {"success": False, "message": result.get("message", "Face not recognized")}
