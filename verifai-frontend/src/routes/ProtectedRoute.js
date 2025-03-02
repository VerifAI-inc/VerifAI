import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ element }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("accessToken"));

  // Function to verify if the token is still valid
  const verifyToken = async () => {
    const accessToken = localStorage.getItem("accessToken");

    if (!accessToken) {
      setIsAuthenticated(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/token/verify/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: accessToken }),
      });

      if (!response.ok) {
        setIsAuthenticated(false);
        localStorage.removeItem("accessToken");
      }
    } catch (error) {
      console.error("Token verification failed:", error);
      setIsAuthenticated(false);
      localStorage.removeItem("accessToken");
    }
  };

  useEffect(() => {
    verifyToken(); // Run token verification when component mounts
  }, []);

  return isAuthenticated ? element : <Navigate to="/login" replace />;
};

export default ProtectedRoute;