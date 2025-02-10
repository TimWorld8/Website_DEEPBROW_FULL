import React, { useState } from "react";
import { UploadCloud } from "lucide-react";
import axios from "axios";

export default function Home() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const handleProcessImage = async () => {
    if (!selectedImage) return;
    setIsProcessing(true);
    const formData = new FormData();
    formData.append("file", selectedImage);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/remove-eyebrow/",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          responseType: "blob",
        }
      );
      const blob = new Blob([response.data], {
        type: response.headers["content-type"],
      });
      setProcessedImage(URL.createObjectURL(blob));
    } catch (error) {
      console.error("Processing failed:", error);
      alert(
        `Processing failed! ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="route-content">
      <main className="flex flex-col items-center justify-center text-center p-4 bg-gradient-to-b from-pink-100 to-white min-h-screen">
        <h1 className="text-5xl font-extrabold text-pink-700 mt-8 animate-bounce">
          Discover Your Perfect Eyebrow Shape
        </h1>
        <p className="max-w-md mx-auto mb-8 text-gray-700 text-lg">
          Using advanced AI technology to enhance your natural beauty and create
          the most flattering eyebrow shape for your unique facial features.
        </p>
        <button
          onClick={() => alert("Start Your Beauty Journey")}
          className="bg-pink-700 text-white px-8 py-4 rounded-full hover:bg-pink-800 transition-all transform hover:scale-105 shadow-lg"
        >
          Start Your Beauty Journey
        </button>

        <div className="upload-container">
          {/* Upload box */}
          <div className="upload-box w-full max-w-md p-8 rounded-2xl shadow-2xl text-gray-900 mt-8 transition-transform transform hover:scale-105">
            <div className="flex flex-col items-center gap-6">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-400 rounded-lg cursor-pointer bg-[#F5F5F5] hover:bg-gray-100 transition-colors">
                <UploadCloud className="text-gray-500 w-12 h-12 animate-pulse" />
                <p className="text-gray-500 mt-2">Upload Image</p>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageUpload}
                />
              </label>
              <button
                className="w-full bg-[#C2185B] text-white rounded-lg p-3 disabled:bg-gray-500 transition-all transform hover:scale-105"
                onClick={handleProcessImage}
                disabled={!selectedImage || isProcessing}
              >
                {isProcessing ? "Processing..." : "Submit Image"}
              </button>
            </div>
          </div>

          {/* Processed result */}
          {processedImage && (
            <div className="result-container mt-8 p-8 rounded-2xl shadow-2xl w-full max-w-md text-gray-900 transition-transform transform hover:scale-105">
              <h2 className="text-lg font-semibold text-center mb-4">Result Remove Eyebrow</h2>
              <img
                src={processedImage}
                alt="Processed Result"
                className="w-full h-64 object-cover rounded-lg"
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
