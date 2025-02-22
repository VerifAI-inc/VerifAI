import React, { useState } from "react";
import "../styles/Profile.css";

const Profile = () => {
  const [activeSection, setActiveSection] = useState("account");

  return (
    <div className="profile-page">
      <div className="profile-container">
        {/* Left Sidebar Menu */}
        <div className="profile-sidebar">
          <h2>Profile</h2>
          <ul>
            <li
              className={activeSection === "account" ? "active" : ""}
              onClick={() => setActiveSection("account")}
            >
              📌 Account Information
            </li>
            <li
              className={activeSection === "reports" ? "active" : ""}
              onClick={() => setActiveSection("reports")}
            >
              📄 Reports
            </li>
          </ul>
        </div>

        {/* Right Content Area */}
        <div className="profile-content">
          <div className={`content-wrapper ${activeSection === "account" ? "fade-in" : "fade-out"}`}>
            {activeSection === "account" && (
              <div className="profile-info">
                <img src="https://i.pravatar.cc/150?img=8" alt="User Avatar" className="profile-avatar" />
                <h2>John Doe</h2>
                <p>Email: johndoe@example.com</p>
                <p>Phone: +123 456 7890</p>
                <p>Joined: January 10, 2023</p>
                <button className="edit-profile-btn">Edit Profile</button>
              </div>
            )}
          </div>

          <div className={`content-wrapper ${activeSection === "reports" ? "fade-in" : "fade-out"}`}>
            {activeSection === "reports" && (
              <div className="profile-reports">
                <h3>User Reports</h3>
                <ul>
                  <li>📄 Report 1 - <span>Feb 20, 2025</span></li>
                  <li>📄 Report 2 - <span>Feb 18, 2025</span></li>
                  <li>📄 Report 3 - <span>Feb 15, 2025</span></li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;