import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');

  if (!token) {
    // If no token, redirect to login page
    return <Navigate to="/" replace />;
  }

  // Otherwise, allow access
  return children;
};

export default ProtectedRoute;
