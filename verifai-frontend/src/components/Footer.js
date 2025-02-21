import React from "react";
import { Link } from "react-router-dom";
import "../styles/components/Footer.css";
import { FaEnvelope } from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Left Section - Brand & Contact */}
        <div className="footer-left">
          <h2>VerifAI</h2>
          <p className="footer-tagline">Ensure fairness, protect privacy, build trust.</p>
          <p>© {new Date().getFullYear()} VerifAI. All rights reserved.</p>
          <p>
            <FaEnvelope className="icon" />
            <a href="mailto:support@verifai.com"> support@verifai.com</a>
          </p>
        </div>

        {/* Center Section - Quick Links */}
        <div className="footer-center">
          <h3>Quick Links</h3>
          <div className="quick-links">
            <ul className="top-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/upload">Upload</Link></li>
              <li><Link to="/results">Results</Link></li>
            </ul>
            <ul className="bottom-links">
              <li><Link to="/reports">Reports</Link></li>
              <li><Link to="/profile">Profile</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><Link to="/signup">Sign Up</Link></li>
            </ul>
          </div>
        </div>

        {/* Right Section - Newsletter Subscription */}
        <div className="footer-right">
          <h3>Stay Updated</h3>
          <div className="footer-line"></div>
          <form className="newsletter-form">
            <input type="email" placeholder="Enter your email" required />
            <button type="submit">Subscribe</button>
          </form>
        </div>
      </div>
    </footer>
  );
};

export default Footer;