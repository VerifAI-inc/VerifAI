import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/components/Navbar.css";
import { FaUserCircle } from "react-icons/fa"; // Import user icon

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Track login state
  const [dropdownOpen, setDropdownOpen] = useState(false); // Track dropdown menu state

  // Handle Logout
  const handleLogout = () => {
    setIsLoggedIn(false);
    setDropdownOpen(false);
  };

  return (
    <nav className="navbar">
      {/* Logo Section */}
      <div className="navbar-logo">
        <span>VerifAI</span>
      </div>

      {/* Menu Links */}
      <ul className={`navbar-links ${menuOpen ? "open" : ""}`}>
        <li><Link to="/" onClick={() => setMenuOpen(false)}>Home</Link></li>
        <li><Link to="/upload" onClick={() => setMenuOpen(false)}>Upload</Link></li>
        <li><Link to="/results" onClick={() => setMenuOpen(false)}>Results</Link></li>
        <li><Link to="/reports" onClick={() => setMenuOpen(false)}>Reports</Link></li>
        <li><Link to="/contact" onClick={() => setMenuOpen(false)}>Contact</Link></li>

        {/* Show Log In or User Profile Dropdown */}
        <li className="user-menu">
          {!isLoggedIn ? (
            <Link to="/login" className="login-button" onClick={() => setIsLoggedIn(true)}>
              Log In
            </Link>
          ) : (
            <div className="user-icon" onClick={() => setDropdownOpen(!dropdownOpen)}>
              <FaUserCircle size={25} />
              {dropdownOpen && (
                <div className="dropdown-menu">
                  <Link to="/profile" onClick={() => setDropdownOpen(false)}>👤 Profile</Link>
                  <Link to="/settings" onClick={() => setDropdownOpen(false)}>⚙ Settings</Link>
                  <button onClick={handleLogout}>🚪 Log Out</button>
                </div>
              )}
            </div>
          )}
        </li>
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