import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import Jatin from "../assets/jatin.jpeg";

// Dummy student data
const students = [
  {
    id: 1,
    name: "Jatin Gupta",
    photo: {Jatin} // local image path
  }
];

const CameraCapture = () => {
  const [selectedStudent, setSelectedStudent] = useState(students[0]); // default student
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);

  // Capture image
  const capture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  };

  // Submit image
  const handleSubmit = () => {
    console.log("Submitting image for:", selectedStudent.name);
    console.log("Captured Image:", capturedImage);

    // Example: send to backend
    fetch("http://localhost:5000/attendance", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        studentId: selectedStudent.id,
        image: capturedImage
      })
    })
      .then((res) => res.json())
      .then((data) => {
        alert("Attendance marked for " + selectedStudent.name);
      })
      .catch((err) => console.error(err));
  };

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      {/* Student Name */}
      <h2>{selectedStudent.name}</h2>

      {/* Show camera if image not captured */}
      {!capturedImage ? (
        <>
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            mirrored={true} // Selfie mode
            style={{ width: "300px", height: "250px", border: "2px solid black" }}
          />
          <br />
          <button onClick={capture} style={{ marginTop: "10px" }}>
            Capture
          </button>
        </>
      ) : (
        <>
          {/* Preview Image */}
          <img
            src={capturedImage}
            alt="captured"
            style={{ width: "300px", height: "250px", border: "2px solid green" }}
          />
          <br />
          <button
            onClick={() => setCapturedImage(null)}
            style={{ margin: "10px" }}
          >
            Retake
          </button>
          <button onClick={handleSubmit}>Submit</button>
        </>
      )}
    </div>
  );
};

export default CameraCapture;
