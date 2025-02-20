import React, { useState } from "react";
import { UploadCloud } from "lucide-react";
import axios from "axios";
import { ImgComparisonSlider } from '@img-comparison-slider/react';
import TermsModal from "./components/TermsModal";

export default function Home({ setIsAccepted }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showTerms, setShowTerms] = useState(true);
  const [selectedStyle, setSelectedStyle] = useState('makeup');
  const [selectedMakeupImage, setSelectedMakeupImage] = useState(null);
  const [selectedEyebrowImage, setSelectedEyebrowImage] = useState(null);

  const makeupStyles = [
    '/src/image/style/style.jpg',
    '/src/image/style/Teardrop-Eyes-Korean-Makeup.png',
    '/src/image/style/style03.jpg',
    '/src/image/style/style04.jpg',
    '/src/image/style/style05.jpg',
    '/src/image/style/style06.jpg',
    '/src/image/style/style07.jpg',
    '/src/image/style/style08.jpg',
    '/src/image/style/style09.jpg',
    '/src/image/style/style10.jpg',
  ];

  const eyebrowStyles = [
    'src/image/eyebrow/flat-rmbg.png',
    'src/image/eyebrow/hardtangle-rmbg.png',
    'src/image/eyebrow/rounded-rmbg.png',
    'src/image/eyebrow/softangle-rmbg.png',
    'src/image/eyebrow/steep_arch-rmbg.png',
    'src/image/eyebrow/straight-rmbg.png',
    'src/image/eyebrow/generate.png',

  ];

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const handleProcessImage = async () => {
    if (!selectedImage) {
      alert("Please select an image first");
      return;
    }
    if (!selectedMakeupImage) {
      alert("Please select a makeup style");
      return;
    }
    if (!selectedEyebrowImage) {
      alert("Please select an eyebrow style");
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    formData.append("file", selectedImage);
    formData.append("style", selectedMakeupImage);
    formData.append("eyebrow", selectedEyebrowImage);
    formData.append("model", Number(0));

    console.log("Sending request with:", {
      file: selectedImage.name,
      style: selectedMakeupImage,
      eyebrow: selectedEyebrowImage,
      model: 0
    });

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
      const errorMessage = error.response?.data instanceof Blob 
        ? await error.response.data.text() 
        : error.response?.data?.detail || error.message;
      console.error("Error details:", errorMessage);
      alert(`Processing failed! ${errorMessage}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="route-content">
      {showTerms && (
        <TermsModal
          onAccept={() => {
            setIsAccepted(true);
            setShowTerms(false);
          }}
          onReject={() => alert("คุณต้องยอมรับเงื่อนไขก่อนใช้บริการ")}
        />
      )}
     
      
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
        
        {processedImage && (
            <div className="result-container mt-8 p-8 rounded-2xl shadow-2xl w-full max-w-md text-gray-900 transition-transform transform hover:scale-105">
              <h2 className="text-lg font-semibold text-center mb-4">Result Remove Eyebrow</h2>
            

              <ImgComparisonSlider>
                <img slot="first" src={selectedImage ? URL.createObjectURL(selectedImage) : ''} />
                <img slot="second" src={processedImage} />
              </ImgComparisonSlider>
            

              {/* <img
                src={processedImage}
                alt="Processed Result"
                className="w-full h-64 object-cover rounded-lg"
              /> */}
            </div>
          )}

        <div className="parent-container">
            {/* กล่อง DESIGN */}
            <div className="design-container">
              <h2 className="text-2xl font-bold text-pink-700 mb-4">DESIGN</h2>
              <div className="flex gap-4">
                <button 
                  className={`${
                    selectedStyle === 'makeup' ? 'bg-yellow-700' : 'bg-yellow-600'
                  } text-white px-4 py-2 rounded hover:bg-yellow-700`}
                  onClick={() => setSelectedStyle('makeup')}
                >
                  MAKEUP STYLE
                </button>
                <button 
                  className={`${
                    selectedStyle === 'eyebrow' ? 'bg-brown-700' : 'bg-brown-600'
                  } text-white px-4 py-2 rounded hover:bg-brown-700`}
                  onClick={() => setSelectedStyle('eyebrow')}
                >
                  EYEBROW STYLE
                </button>
              </div>
              <div className="design-images grid grid-cols-2 gap-4 mt-4">
                {(selectedStyle === 'makeup' ? makeupStyles : eyebrowStyles).map((image, index) => (
                  <img 
                    key={index}
                    src={image} 
                    alt={`Style ${index + 1}`} 
                    className={`design-image ${
                      (selectedStyle === 'makeup' && selectedMakeupImage === image) ||
                      (selectedStyle === 'eyebrow' && selectedEyebrowImage === image)
                        ? 'selected-image'
                        : ''
                    }`} 
                    onClick={() => {
                      if (selectedStyle === 'makeup') {
                        setSelectedMakeupImage(image);
                      } else {
                        setSelectedEyebrowImage(image);
                      }
                    }}
                  />
                ))}
              </div>
             
            </div>

            {/* กล่อง Upload Image */}
            <div className="upload-container">
            <div className="upload-box w-full max-w-md p-8 rounded-2xl shadow-2xl text-gray-900 mt-8 transition-transform transform hover:scale-105">
            <UploadCloud className="text-gray-500 w-12 h-12 animate-pulse" />
              <h3 className="text-xl font-bold text-gray-700 mb-4">Upload Image</h3>
              <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageUpload}
                />
              <button
                className="w-full bg-[#C2185B] text-white rounded-lg p-3 disabled:bg-gray-500 transition-all transform hover:scale-105"
                onClick={handleProcessImage}
                disabled={!selectedImage || isProcessing}
              >
                {isProcessing ? "Processing..." : "Submit Image"}
              </button>
            </div>
            </div>
            </div>
    

       
          
          
        
      </main>

      {/* Add CSS for the glow effect */}
      <style jsx>{`
        .selected-image {
          box-shadow: 0 0 10px 5px rgba(255, 105, 180, 0.8);
          border-radius: 8px;
        }
      `}</style>
    </div>
  );
}
