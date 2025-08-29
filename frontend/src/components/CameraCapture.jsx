import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

const CameraCapture = () => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);

  const capture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  };

  const handleSubmit = async () => {
    if (!capturedImage) return alert("Capture an image first!");

    // Convert base64 to Blob/File
    const byteString = atob(capturedImage.split(",")[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: "image/jpeg" });
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("studentId", 123); // Example student ID

    try {
      const res = await fetch("http://127.0.0.1:8000/attendance", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log(data);
      alert(data.message);
    } catch (err) {
      console.error(err);
      alert("Error sending image to backend!");
    }
  };

  return (
    <div>
      <Webcam audio={false} ref={webcamRef} screenshotFormat="image/jpeg" />
      <button onClick={capture}>Capture</button>
      {capturedImage && <img src={capturedImage} alt="Captured" width={200} />}
      <button onClick={handleSubmit}>Submit Attendance</button>
    </div>
  );
};

export default CameraCapture;
