import React, { useEffect } from 'react';
import './TermsModal.css';

const TermsModal = ({ onAccept, onReject }) => {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div className="terms-modal__overlay">
      <div className="terms-modal__container">
        <h2 className="terms-modal__title">ข้อตกลงและเงื่อนไขการใช้บริการ</h2>
        <p className="terms-modal__content">
          ระบบนี้มีการเก็บข้อมูลรูปภาพของคุณเพื่อพัฒนาคุณภาพการให้บริการ
          และอาจมีการนำข้อมูลไปใช้เพื่อการวิจัยและปรับปรุงเทคโนโลยีในอนาคต
        </p>
        <div className="terms-modal__buttons">
          <button onClick={onReject} className="terms-modal__reject-btn">ปฏิเสธ</button>
          <button onClick={onAccept} className="terms-modal__accept-btn">ยอมรับ</button>
        </div>
      </div>
    </div>
  );
};

export default TermsModal;