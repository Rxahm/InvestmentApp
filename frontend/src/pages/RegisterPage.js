import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../Services/api";

const RegisterPage = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("owner");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await API.post("register/", {
        username: username.trim(),
        email: email.trim(),
        password,
        role,
      });

      setSuccess("Account created. You can now sign in.");
      setUsername("");
      setEmail("");
      setPassword("");
      setRole("owner");

      setTimeout(() => navigate("/"), 1200);
    } catch (err) {
      const message = err.response?.data?.error || "Registration failed. Please review your details.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "60px auto", textAlign: "center" }}>
      <h1>Create an account</h1>
      <p style={{ color: "#4c4c4c", marginTop: 8 }}>Use your details to access the Pretium Investment portal.</p>

      {error && (
        <p style={{ color: "#b00020", marginTop: 16 }} role="alert">
          {error}
        </p>
      )}

      {success && (
        <p style={{ color: "#0f5a44", marginTop: 16 }} role="status">
          {success}
        </p>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 24 }}>
        <input
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        <select value={role} onChange={(event) => setRole(event.target.value)}>
          <option value="owner">Owner</option>
          <option value="accountant">Accountant</option>
        </select>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p style={{ marginTop: 24 }}>
        Already registered? <Link to="/">Back to sign in</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
