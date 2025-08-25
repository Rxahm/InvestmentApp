import React, { useState } from 'react';
import API from '../Services/api'; // Central Axios service

const Generate2FA = () => {
  const [qrCode, setQrCode] = useState(null);
  const [error, setError] = useState('');

  const fetch2FA = async () => {
    try {
      const response = await API.get('/generate-2fa/');
      setQrCode(response.data.qr_code); // assuming backend returns 'qr_code' base64
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to generate QR code.');
    }
  };

  return (
    <div>
      <h2>Generate 2FA QR Code</h2>
      <button onClick={fetch2FA}>Generate 2FA</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {qrCode && (
        <div>
          <h3>Scan This QR Code</h3>
          <img src={`data:image/png;base64,${qrCode}`} alt="2FA QR Code" />
        </div>
      )}
    </div>
  );
};

export default Generate2FA;
