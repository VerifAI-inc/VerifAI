import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/pages/Login.css";

const Login = () => {
  const [formData, setFormData] = useState({
    userInput: "",
    password: "",
  });

  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
  
    const requestData = {
      username: formData.userInput,
      password: formData.password,
    };
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });
  
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("refreshToken", data.refresh_token);
        localStorage.setItem("username", requestData.username);
        window.dispatchEvent(new Event("storage"));
        navigate("/profile");
      } else {
        // Try to parse error JSON if available
        let errorMessage = "Invalid login credentials.";
        try {
          const data = await response.json();
          if (data?.error) {
            errorMessage = data.error;
          }
        } catch (jsonErr) {
          // Body wasn't JSON – keep fallback
        }
        setError(errorMessage);
      }
    } catch (err) {
      setError("Server error. Please try again later.");
    }
  };
  

  return (
    <div className="login-page">
      {/* Page Header */}
      <section className="login-header">
        <div className="login-container">
          {/* <h2>VerifAI</h2> */}
          <div className="login-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>LOGIN</span>
          </div>
        </div>
      </section>

      {/* Login Form */}
      <section className="login-form-section">
        <h1 className="login-title">Sign In</h1>
        {error && <p className="error-message">{error}</p>}
        <form className="login-form" onSubmit={handleSubmit}>
          {/* Email or Username */}
          <div className="login-form-group">
            <label>
              Email or Username <span className="login-required">*</span>
            </label>
            <input
              type="text"
              name="userInput"
              placeholder="Enter your email or username"
              required
              onChange={handleChange}
            />
          </div>

          {/* Password */}
          <div className="login-form-group">
            <label>
              Password <span className="login-required">*</span>
            </label>
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
            <p>
              Don't have an account?  
              <Link to="/signup" className="login-signup-link"> Sign up here</Link>.
            </p>
          </div>

          {/* Forgot Password */}
          <div className="login-forgot-password">
            <Link to="/forgotpassword">Forgot password?</Link>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Login;
