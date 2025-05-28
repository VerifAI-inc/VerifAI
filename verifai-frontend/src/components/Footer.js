import React from "react";
import { Link } from "react-router-dom";
import "../styles/components/Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">

        {/* Column 1 - Left */}
        <div className="footer-left">
          <h2>VerifAI</h2>
          <p className="footer-tagline">Ensure fairness, protect privacy, build trust.</p>
        </div>

        {/* Column 2 - Center */}
        <div className="footer-center">
          <h3>Quick Links</h3>
          <div className="quick-links">
            <ul className="top-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/services">Services</Link></li>
              <li><Link to="/upload">Upload</Link></li>
            </ul>
            <ul className="bottom-links">
              <li><Link to="/profile">Profile</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><Link to="/login">Login</Link></li>
            </ul>
          </div>
        </div>

        {/* Column 3 - Right */}
        <div className="footer-right">
          <h3>Stay Updated</h3>
          <form className="newsletter-form">
            <input type="email" placeholder="Enter your email" required />
            <button type="submit">Subscribe</button>
          </form>
        </div>

        {/* Column 4 - Contact Info */}
        <div className="footer-contact">
          <h3>Contact</h3>

          {/* Email - Keep full text */}
          <div className="footer-social-inline">
            <i className="fas fa-envelope icon"></i>
            <a href="mailto:info@verifai.tech">info@verifai.tech</a>
          </div>

          {/* Social icons - Just logos side by side */}
          <div className="footer-social-icons">
            <a href="https://www.instagram.com/verifai.tech" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-instagram icon"></i>
            </a>
            <a href="https://www.linkedin.com/company/verif-ai" target="_blank" rel="noopener noreferrer">
              <i className="fab fa-linkedin icon"></i>
            </a>
          </div>
        </div>

      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} VerifAI. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
