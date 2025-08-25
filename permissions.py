// frontend/src/pages/LoginPage.js

import React, { useState } from 'react';
import API from '../Services/api';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(''); // 2FA token
  const [error, setError] = useState('');

  const handleLogin = async () => {
    try {
      const response = await API.post('/login/', { username, password, token });
      console.log(response.data);
      // Save JWT tokens or redirect user
    } catch (err) {
      setError(err.response?.data?.error || "Login failed.");
    }
  };

  return (
    <div>
      <h1>Login</h1>
      {error && <p style={{color: "red"}}>{error}</p>}
      <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <input placeholder="2FA Token" value={token} onChange={e => setToken(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default LoginPage;
