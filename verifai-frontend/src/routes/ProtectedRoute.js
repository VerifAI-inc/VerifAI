import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ element }) => {
  const isAuthenticated = !!localStorage.getItem("authToken"); // Check if user is logged in

  return isAuthenticated ? element : <Navigate to="/login" replace />;
};

export default ProtectedRoute;