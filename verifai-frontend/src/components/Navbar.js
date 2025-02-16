import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav style={{ display: "flex", alignItems: "center", padding: "10px", borderBottom: "1px solid #ccc" }}>
      {/* Logo Placeholder */}
      <div style={{ marginRight: "15px" }}>
        <img src="/logo.png" alt="VerifAI Logo" style={{ height: "40px" }} />
      </div>

      {/* Navigation Links */}
      <ul style={{ listStyle: "none", display: "flex", gap: "15px" }}>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/upload">Upload</Link></li>
        <li><Link to="/profile">Profile</Link></li>
        <li><Link to="/contact">Contact</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;