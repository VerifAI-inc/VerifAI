import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "../styles/pages/ForgotPassword.css";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);

    // Simulate API call with a delay
    setTimeout(() => {
      console.log("Reset Password for:", email);
    }, 2000);
  };

  return (
    <div className="forgot-password-page">
      <div className="forgot-password-container">
        {/* Left Section */}
        <div className="forgot-password-left">
          <h2>Forgot Your Password?</h2>
          <p>No worries! Enter your email and we'll send you a reset link.</p>
        </div>

        {/* Right Section */}
        <div className="forgot-password-right">
          {!submitted ? (
            <>
              <h1 className="forgot-password-title">Reset Password</h1>
              <form className="forgot-password-form" onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Email Address <span className="required">*</span></label>
                  <input
                    type="email"
                    name="email"
                    placeholder="Enter your registered email"
                    required
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>

                <button type="submit" className="forgot-password-button">Send Reset Link</button>

                <div className="forgot-password-footer">
                  <p>Remember your password?  
                    <Link to="/login" className="login-link"> Log in</Link>.
                  </p>
                </div>
              </form>
            </>
          ) : (
            <div className="success-message">
              <h2>🎉 Reset Link Sent!</h2>
              <p>Check your email for instructions to reset your password.</p>
              <Link to="/login" className="go-back-button">Go to Login</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;