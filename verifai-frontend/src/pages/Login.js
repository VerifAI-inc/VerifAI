import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/pages/Login.css";

const Login = () => {
  const [formData, setFormData] = useState({
    userInput: "",
    password: "",
  });

  const [error, setError] = useState(null);
  const navigate = useNavigate(); // Hook for navigation

  // Mouse Light Effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      const { clientX: x, clientY: y } = e;
      document.documentElement.style.setProperty("--mouseX", `${x}px`);
      document.documentElement.style.setProperty("--mouseY", `${y}px`);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
  
    const requestData = {
      username: formData.userInput, // Adjust based on backend handling
      password: formData.password,
    };
  
    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });
  
      const data = await response.json();
      if (response.ok) {
        // Store JWT tokens in localStorage
        localStorage.setItem("accessToken", data.access_token);
        localStorage.setItem("refreshToken", data.refresh_token);
        localStorage.setItem("username", requestData.username);
  
        // Dispatch event to trigger Navbar update
        window.dispatchEvent(new Event("storage"));
  
        // Redirect to profile page
        navigate("/profile");
      } else {
        setError(data.error || "Invalid login credentials.");
      }
    } catch (err) {
      setError("Server error. Please try again later.");
    }
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
        {error && <p className="error-message">{error}</p>}
        <form className="login-form" onSubmit={handleSubmit}>
          {/* Email or Username */}
          <div className="form-group">
            <label>Email or Username <span className="required">*</span></label>
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

          <div className="login-footer">
            <p>Forgot your password?  
              <Link to="/forgotpassword" className="forgot-password-link"> Reset it</Link>.
            </p>
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