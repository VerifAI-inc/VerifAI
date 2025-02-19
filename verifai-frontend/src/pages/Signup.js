import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/Signup.css";

const Signup = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    console.log("Sign Up Data:", formData);
  };

  return (
    <div className="signup-container">
      {/* Left Side (Branding) */}
      <div className="signup-left">
        <h2>Welcome to VerifAI!</h2>
        <p>Ensure fairness, protect privacy, build trust.</p>
      </div>

      {/* Right Side: Signup Form */}
      <div className="signup-right">
        <h1 className="signup-title">Create an Account</h1>
        <form className="signup-form" onSubmit={handleSubmit}>

          {/* First Row - First Name & Last Name */}
          <div className="row">
            <div className="form-group">
              <label>First Name <span className="required">*</span></label>
              <input type="text" name="firstName" placeholder="Enter first name" required onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Last Name <span className="required">*</span></label>
              <input type="text" name="lastName" placeholder="Enter last name" required onChange={handleChange} />
            </div>
          </div>

          {/* Second Row - Username & Email */}
          <div className="row">
            <div className="form-group">
              <label>Username <span className="required">*</span></label>
              <input type="text" name="username" placeholder="Choose a username" required onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Email <span className="required">*</span></label>
              <input type="email" name="email" placeholder="Enter your email" required onChange={handleChange} />
            </div>
          </div>

          {/* Third Row - Password & Confirm Password */}
          <div className="row">
            <div className="form-group">
              <label>Password <span className="required">*</span></label>
              <input type="password" name="password" placeholder="Enter your password" required onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Confirm Password <span className="required">*</span></label>
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
      </div>
    </div>
  );
};

export default Signup;
