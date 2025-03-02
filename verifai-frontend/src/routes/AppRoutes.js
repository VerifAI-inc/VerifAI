import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Upload from "../pages/Upload";
import Results from "../pages/Results";
import Reports from "../pages/Reports";
import Profile from "../pages/Profile";
import Contact from "../pages/Contact";
import Tables from "../pages/Tables";  
import ForgotPassword from "../pages/ForgotPassword";
import ProtectedRoute from "./ProtectedRoute"; // Import ProtectedRoute
import PublicRoute from "./PublicRoute"; // Import PublicRoute

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      
      {/* Public Routes (Prevent access if already logged in) */}
      <Route path="/login" element={<PublicRoute element={<Login />} />} />
      <Route path="/signup" element={<PublicRoute element={<Signup />} />} />
      
      {/* Protected Routes (Require login) */}
      <Route path="/upload" element={<ProtectedRoute element={<Upload />} />} />
      <Route path="/results" element={<ProtectedRoute element={<Results />} />} />
      <Route path="/reports" element={<ProtectedRoute element={<Reports />} />} />
      <Route path="/profile" element={<ProtectedRoute element={<Profile />} />} />
      <Route path="/tables" element={<ProtectedRoute element={<Tables />} />} />
      
      {/* Public Route (Anyone can access) */}
      <Route path="/contact" element={<Contact />} />
      <Route path="/forgotpassword" element={<ForgotPassword />} />
    </Routes>
  );
};

export default AppRoutes;