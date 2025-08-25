import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // We need react-router-dom installed
import API from '../Services/api'; // Central axios instance

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate(); // <-- this will help us redirect

  const handleLogin = async () => {
    try {
      const response = await API.post('/login/', { username, password, token });
      console.log(response.data);

      // Save access token
      localStorage.setItem('access_token', response.data.access);

      // Clear form and errors
      setUsername('');
      setPassword('');
      setToken('');
      setError('');

      // Redirect to Dashboard
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Login failed.");
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Login</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ margin: '10px' }}>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
      </div>

      <div style={{ margin: '10px' }}>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
      </div>

      <div style={{ margin: '10px' }}>
        <input
          placeholder="2FA Token"
          value={token}
          onChange={e => setToken(e.target.value)}
        />
      </div>

      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default LoginPage;
