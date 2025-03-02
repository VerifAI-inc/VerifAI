import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/components/Navbar.css";
import { FaUserCircle } from "react-icons/fa"; // Import user icon

const Navbar = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("authToken")); // Initial state check
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Handle Logout
  const handleLogout = async () => {
  try {
    const refreshToken = localStorage.getItem("refreshToken");

    await fetch("http://127.0.0.1:8000/auth/logout/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } catch (error) {
    console.error("Logout failed:", error);
  }

  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("username");
  setIsLoggedIn(false);
  navigate("/");
};

  // Ensure Navbar updates when login state changes
  useEffect(() => {
    const handleStorageChange = () => {
      setIsLoggedIn(!!localStorage.getItem("authToken"));
    };

    // Listen for changes in localStorage
    window.addEventListener("storage", handleStorageChange);
    
    // Check state again when the component mounts
    handleStorageChange();

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

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
            <Link to="/login" className="login-button">
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