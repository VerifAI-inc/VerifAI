import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/Login.css";

const Login = () => {
  const [formData, setFormData] = useState({
    userInput: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login Data:", formData);
  };

  return (
    <div className="login-container">
      {/* Left Side (Branding) */}
      <div className="login-left">
        <h2>Welcome Back!</h2>
        <p>Log in and continue your VerifAI journey.</p>
      </div>

      {/* Right Side: Login Form */}
      <div className="login-right">
        <h1 className="login-title">Sign In</h1>
        <form className="login-form" onSubmit={handleSubmit}>
          {/* Email or Username */}
          <div className="form-group">
            <label>Enter Email or Username <span className="required">*</span></label>
            <input 
              type="text" 
              name="userInput" 
              placeholder="Enter your email or username" 
              required 
              onChange={handleChange} 
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label>Password <span className="required">*</span></label>
            <input 
              type="password" 
              name="password" 
              placeholder="Enter your password" 
              required 
              onChange={handleChange} 
            />
          </div>

          {/* Login Button */}
          <button type="submit" className="login-button">Login</button>

          {/* Signup Redirect */}
          <div className="login-footer">
            <p>Don't have an account?  
              <Link to="/signup" className="signup-link"> Sign up here</Link>.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;