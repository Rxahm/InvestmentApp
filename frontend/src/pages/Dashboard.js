import React from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  return (
    <div style={{ maxWidth: 720, margin: "60px auto" }}>
      <h1>Welcome to the dashboard</h1>
      <p>You are logged in. Use the links below to continue.</p>
      <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
        <button type="button" onClick={() => navigate("/settings/2fa")}>Manage 2FA</button>
        <button type="button" onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
};

export default Dashboard;
