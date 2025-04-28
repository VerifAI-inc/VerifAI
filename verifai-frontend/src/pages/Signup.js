import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/pages/Signup.css";

const Signup = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    const requestData = {
      username: formData.username,
      password: formData.password,
      email: formData.email,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("Signup successful! Redirecting...");
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        setError(data.error || "Signup failed. Try again.");
      }
    } catch (err) {
      setError("Server error. Please try again later.");
    }
  };

  return (
    <div className="signup-page">
      {/* Page Header */}
      <section className="signup-header">
        <div className="signup-container">
          {/* <h2>VerifAI</h2> */}
          <div className="signup-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>SIGN UP</span>
          </div>
        </div>
      </section>

      {/* Signup Form Section */}
      <section className="signup-form-section">
        <h1 className="signup-title">Create an Account</h1>

        {/* ✅ Display messages */}
        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}

        <form className="signup-form" onSubmit={handleSubmit}>
          {/* First Row - First Name & Last Name */}
          <div className="signup-row">
            <div className="signup-form-group">
              <label>First Name <span className="signup-required">*</span></label>
              <input type="text" name="firstName" placeholder="Enter first name" required onChange={handleChange} />
            </div>
            <div className="signup-form-group">
              <label>Last Name <span className="signup-required">*</span></label>
              <input type="text" name="lastName" placeholder="Enter last name" required onChange={handleChange} />
            </div>
          </div>

          {/* Second Row - Username & Email */}
          <div className="signup-row">
            <div className="signup-form-group">
              <label>Username <span className="signup-required">*</span></label>
              <input type="text" name="username" placeholder="Choose a username" required onChange={handleChange} />
            </div>
            <div className="signup-form-group">
              <label>Email <span className="signup-required">*</span></label>
              <input type="email" name="email" placeholder="Enter your email" required onChange={handleChange} />
            </div>
          </div>

          {/* Third Row - Password & Confirm Password */}
          <div className="signup-row">
            <div className="signup-form-group">
              <label>Password <span className="signup-required">*</span></label>
              <input type="password" name="password" placeholder="Enter your password" required onChange={handleChange} />
            </div>
            <div className="signup-form-group">
              <label>Confirm Password <span className="signup-required">*</span></label>
              <input type="password" name="confirmPassword" placeholder="Re-enter your password" required onChange={handleChange} />
            </div>
          </div>

          {/* Sign Up Button */}
          <button type="submit" className="signup-button">Sign Up</button>

          {/* Login Redirect */}
          <div className="signup-footer">
            <p>Already have an account?
              <Link to="/login" className="login-link"> Log in here</Link>.
            </p>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Signup;
