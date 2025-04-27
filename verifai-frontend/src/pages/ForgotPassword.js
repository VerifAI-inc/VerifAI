import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/pages/Login.css"; 

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/forgot-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitted(true);
      } else {
        setError(data.error || "Something went wrong.");
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
          <h2>VerifAI</h2>
          <div className="login-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>FORGOT PASSWORD</span>
          </div>
        </div>
      </section>

      {/* Forgot Password Form */}
      <section className="login-form-section">
        {!submitted ? (
          <>
            <h1 className="login-title">Reset Password</h1>

            {error && <p className="error-message">{error}</p>}

            <form className="login-form" onSubmit={handleSubmit}>
              <div className="login-form-group">
                <label>
                  Email Address <span className="login-required">*</span>
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your registered email"
                  required
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <button type="submit" className="login-button">Send Reset Link</button>

              <div className="login-footer">
                <p>
                  Remember your password?
                  <Link to="/login" className="login-signup-link"> Log in</Link>.
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
      </section>
    </div>
  );
};

export default ForgotPassword;
