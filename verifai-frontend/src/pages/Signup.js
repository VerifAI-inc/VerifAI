import React, { useState, useEffect } from "react";
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
    setSuccess(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    // Prepare request payload
    const requestData = {
      username: formData.username,
      password: formData.password,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/signup/", {
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
          window.location.href = "/login"; // Redirect to login page
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
      <div className="signup-container">
        {/* Left Side (Branding) */}
        <div className="signup-left">
          <h2>Welcome to VerifAI!</h2>
          <p>Ensure fairness, protect privacy, build trust.</p>
        </div>

        {/* Right Side: Signup Form */}
        <div className="signup-right">
          <h1 className="signup-title">Create an Account</h1>
          {error && <p className="error-message">{error}</p>}
          {success && <p className="success-message">{success}</p>}
          <form className="signup-form" onSubmit={handleSubmit}>
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

            <div className="row">
              <div className="form-group">
                <label>Password <span className="required">*</span></label>
                <input type="password" name="password" placeholder="Enter your password" required onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Confirm Password <span className="required">*</span></label>
                <input type="password" name="confirmPassword" placeholder="Confirm password" required onChange={handleChange} />
              </div>
            </div>

            <button type="submit" className="signup-button">Sign Up</button>

            <div className="login-footer">
                        <p>Already have an account?  
                          <Link to="/login" className="login-link"> Log in here</Link>.
                        </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Signup;