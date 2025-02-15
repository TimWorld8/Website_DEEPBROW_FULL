import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Home";
import Compressor from 'compressorjs';

function OurTechnology() {
  return (
    <div className="flex flex-col items-center justify-center mt-8 p-4">
      <h2 className="text-2xl font-bold text-pink-700 mb-4">Our Technology</h2>
      <p className="max-w-xl text-center text-gray-700">
        อธิบายเทคโนโลยี AI ที่ใช้ในการประมวลผล เช่น การตรวจจับโครงหน้า (Facial Landmark Detection)
        และการสร้าง/ลบโครงคิ้ว (Eyebrow Segmentation) เพื่อปรับให้เหมาะสมกับแต่ละบุคคล
      </p>
    </div>
  );
}

function BeautyTips() {
  return (
    <div className="flex flex-col items-center justify-center mt-8 p-4">
      <h2 className="text-2xl font-bold text-pink-700 mb-4">Beauty Tips</h2>
      <p className="max-w-xl text-center text-gray-700">
        แชร์เคล็ดลับความงามต่าง ๆ เกี่ยวกับคิ้ว เช่น วิธีการกันคิ้วให้เข้ากับรูปหน้า,
        เทคนิคการแต่งคิ้วให้ดูเป็นธรรมชาติ ฯลฯ
      </p>
    </div>
  );
}

function Contact() {
  const [image, setImage] = React.useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const result = await compressImage(file);
        const reader = new FileReader();
        reader.onloadend = () => {
          setImage(reader.result);
        };
        reader.readAsDataURL(result);
      } catch (err) {
        console.error(err.message);
      }
    }
  };

  const compressImage = (file) => {
    return new Promise((resolve, reject) => {
      new Compressor(file, {
        quality: 1.0, // Keep quality at 100%
        success: resolve,
        error: reject,
      });
    });
  };

  return (
    <div className="flex flex-col items-center justify-center mt-8 p-4">
      <h2 className="text-2xl font-bold text-pink-700 mb-4">Contact Us</h2>
      <p className="max-w-xl text-center text-gray-700">
        ติดต่อเราสำหรับข้อมูลเพิ่มเติมหรือสอบถามปัญหาได้ตามช่องทางนี้
      </p>
      <form className="max-w-md w-full mt-4">
        <div className="mb-4">
          <label className="block mb-1 text-gray-600">ชื่อ</label>
          <input
            type="text"
            className="w-full border rounded p-2"
            placeholder="กรอกชื่อของคุณ"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-gray-600">อีเมล</label>
          <input
            type="email"
            className="w-full border rounded p-2"
            placeholder="กรอกอีเมลของคุณ"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-gray-600">ข้อความ</label>
          <textarea
            className="w-full border rounded p-2"
            rows="4"
            placeholder="พิมพ์ข้อความ..."
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-gray-600">อัพโหลดรูปภาพ</label>
          <input
            type="file"
            className="w-full border rounded p-2"
            accept="image/*"
            onChange={handleImageUpload}
          />
        </div>
        {image && (
          <div className="result-container mb-4">
            <img src={image} alt="Uploaded" className="image-preview" />
          </div>
        )}
        <button className="bg-pink-700 text-white px-4 py-2 rounded hover:bg-pink-800">
          ส่งข้อความ
        </button>
      </form>
    </div>
  );
}

function Design() {
  return (
    <div className="design-container flex items-center justify-center mt-8 p-4">
      {/* ส่วนของรูปภาพการออกแบบทางด้านซ้าย */}
      <div className="design-section flex flex-col items-center bg-white p-4 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-pink-700 mb-4">DESIGN</h2>
        <div className="flex gap-4">
          <button className="design-button bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700">
            MAKEUP STYLE
          </button>
          <button className="design-button bg-brown-600 text-white px-4 py-2 rounded hover:bg-brown-700">
            EYEBROW STYLE
          </button>
        </div>
        <div className="design-images grid grid-cols-2 gap-4 mt-4">
          {/* เพิ่มรูปภาพ */}
          <img src="/path/to/image1.jpg" alt="Style 1" className="design-image" />
          <img src="/path/to/image2.jpg" alt="Style 2" className="design-image" />
          <img src="/path/to/image3.jpg" alt="Style 3" className="design-image" />
          <img src="/path/to/image4.jpg" alt="Style 4" className="design-image" />
        </div>
      </div>

      {/* ส่วนของอัปโหลดรูปภาพ อยู่ตรงกลาง */}
      <div className="upload-section flex flex-col items-center bg-white p-6 rounded-lg shadow-md ml-8">
        <h3 className="text-xl font-bold text-gray-700 mb-4 text-center">Upload Image</h3>
        <input type="file" className="w-full border rounded p-2" accept="image/*" />
        <button className="mt-4 w-full bg-pink-700 text-white px-4 py-2 rounded hover:bg-pink-800">
          Submit Image
        </button>
      </div>
    </div>
  );
}

function Navbar({ isAccepted }) {
  return (
    <nav className="relative bg-gradient-to-r from-pink-500 via-red-500 to-pink-500 text-white p-6 shadow-lg">
      <div className="absolute inset-0 bg-cover bg-center opacity-20" style={{ backgroundImage: "url('/path/to/your/background-image.jpg')" }}></div>
      <div className="relative max-w-6xl mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <Link to="/" className={`font-extrabold text-3xl hover:text-white transition-colors ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            DEEP BROW
          </Link>
        </div>
        <div className="nav-links flex gap-6">
          <Link to="/" className={`hover:text-white transition-colors text-lg ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            Home
          </Link>
          <Link to="/technology" className={`hover:text-white transition-colors text-lg ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            Our Technology
          </Link>
          <Link to="/tips" className={`hover:text-white transition-colors text-lg ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            Beauty Tips
          </Link>
          <Link to="/contact" className={`hover:text-white transition-colors text-lg ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            Contact
          </Link>
          <Link to="/design" className={`hover:text-white transition-colors text-lg ${!isAccepted ? 'pointer-events-none opacity-50' : ''}`}>
            Design
          </Link>
        </div>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="bg-gradient-to-r from-pink-200 to-pink-100 text-center text-pink-700 p-4 mt-8 shadow-inner">
      <p>© 2025 Deep Brow - By TimWorld</p>
    </footer>
  );
}

export default function App() {
  const [isAccepted, setIsAccepted] = React.useState(false);

  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar isAccepted={isAccepted} />
        <div className="flex-grow">
          <Routes>
            <Route path="/" element={<Home setIsAccepted={setIsAccepted} />} />
            <Route path="/technology" element={<OurTechnology />} />
            <Route path="/tips" element={<BeautyTips />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/design" element={<Design />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}
