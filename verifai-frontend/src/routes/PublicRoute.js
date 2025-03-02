import React from "react";
import { Navigate } from "react-router-dom";

const PublicRoute = ({ element }) => {
  const isAuthenticated = !!localStorage.getItem("authToken"); // Check if user is logged in

  return isAuthenticated ? <Navigate to="/profile" replace /> : element;
};

export default PublicRoute;