import React, { useState } from "react";
import API from "../Services/api";

const Generate2FA = () => {
  const [qrCode, setQrCode] = useState(null);
  const [otpUri, setOtpUri] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const fetch2FA = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await API.get("generate-2fa/");
      setQrCode(response.data.qr_code_base64);
      setOtpUri(response.data.otp_uri);
    } catch (err) {
      const message = err.response?.data?.detail || "Failed to generate a QR code.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "60px auto", textAlign: "center" }}>
      <h2>Two-factor authentication</h2>
      <p>Generate a QR code to enrol a TOTP authenticator such as Google Authenticator.</p>
      <button type="button" onClick={fetch2FA} disabled={isLoading}>
        {isLoading ? "Generating..." : "Generate 2FA QR"}
      </button>

      {error && (
        <p style={{ color: "#b00020", marginTop: 24 }} role="alert">
          {error}
        </p>
      )}

      {qrCode && (
        <div style={{ marginTop: 32 }}>
          <h3>Scan this QR code</h3>
          <img
            src={`data:image/png;base64,${qrCode}`}
            alt="Two-factor authentication QR code"
            style={{ width: 220, height: 220 }}
          />
          <p style={{ marginTop: 16, wordBreak: "break-all" }}>OTP URI: {otpUri}</p>
        </div>
      )}
    </div>
  );
};

export default Generate2FA;
