import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/Navbar.css";
// import logo from "../assets/logo.png"; 

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="navbar">
      {/* Logo Section */}
      <div className="navbar-logo">
        {/* <img src={logo} alt="VerifAI Logo" /> */}
        <span>VerifAI</span>
      </div>

      {/* Menu Links */}
      <ul className={`navbar-links ${menuOpen ? "open" : ""}`}>
        <li><Link to="/" onClick={() => setMenuOpen(false)}>Home</Link></li>
        <li><Link to="/upload" onClick={() => setMenuOpen(false)}>Upload</Link></li>
        <li><Link to="/results" onClick={() => setMenuOpen(false)}>Results</Link></li>
        <li><Link to="/tables" onClick={() => setMenuOpen(false)}>Tables</Link></li>
        <li><Link to="/reports" onClick={() => setMenuOpen(false)}>Reports</Link></li>
        <li><Link to="/profile" onClick={() => setMenuOpen(false)}>Profile</Link></li>
        <li><Link to="/contact" onClick={() => setMenuOpen(false)}>Contact</Link></li>
        <li><Link to="/signup" onClick={() => setMenuOpen(false)}>Sign Up</Link></li>
      </ul>

      {/* Mobile Menu Toggle */}
      <div className="menu-icon" onClick={() => setMenuOpen(!menuOpen)}>
        <div className={`bar ${menuOpen ? "open" : ""}`}></div>
        <div className={`bar ${menuOpen ? "open" : ""}`}></div>
        <div className={`bar ${menuOpen ? "open" : ""}`}></div>
      </div>
    </nav>
  );
};

export default Navbar;
