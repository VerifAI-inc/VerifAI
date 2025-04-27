import React, { useState, useEffect, useRef } from "react";
import "../styles/pages/Profile.css";
import axios from "axios";
import member4 from "../assets/images/member4.jpg";
import { Link, useNavigate } from "react-router-dom";
import {
  FaSearch,
  FaUserCircle,
  FaUser,
  FaEdit,
  FaSignOutAlt,
} from "react-icons/fa";

const Profile = () => {
  const [reports, setReports] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);

  const [editMode, setEditMode] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    surname: "",
    email: "",
  });

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/auth/user/profile/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      .then((res) => setUserInfo(res.data))
      .catch((err) => console.error("Failed to load user info", err));
  }, []);

  // Fetch reports on component mount
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/reports/")
      .then((response) => {
        setReports(response.data);
      })
      .catch((error) => {
        console.error("Error fetching report history:", error);
      });
  }, []);

  // Filter reports based on search term
  const filteredReports = reports.filter((report) =>
    report.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="profile-page">
      {/* Profile Header Section */}
      <section className="profile-header">
        <div className="profile-container">
          <h2>VERIFAI</h2>
          <div className="profile-page-tab">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>PROFILE</span>
          </div>
        </div>
      </section>

      {/* Profile Main Section */}
      <section className="profile-main">
        {/* Left Side (User Information) */}
        <div className="profile-left">
          <img src={member4} alt="Profile" className="profile-image" />
          {userInfo ? (
            <>
              {!editMode ? (
                <>
                  <h1 className="profile-name">
                    {userInfo.name} {userInfo.surname}
                  </h1>
                  <p className="profile-username">@{userInfo.username}</p>
                  <p className="profile-bio">
                    Building AI models for fairness and privacy.
                  </p>
                  <p className="profile-location">📍 Baku, Azerbaijan</p>
                  <p className="profile-email">📧 {userInfo.email}</p>
                </>
              ) : (
                <div className="edit-profile-form">
                  <h3>Edit Profile</h3>
                  <table>
                    <tbody>
                      <tr>
                        <td>Name:</td>
                        <td>
                          <input
                            value={editForm.name}
                            onChange={(e) =>
                              setEditForm({ ...editForm, name: e.target.value })
                            }
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>Surname:</td>
                        <td>
                          <input
                            value={editForm.surname}
                            onChange={(e) =>
                              setEditForm({
                                ...editForm,
                                surname: e.target.value,
                              })
                            }
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>Email:</td>
                        <td>
                          <input
                            type="email"
                            value={editForm.email}
                            onChange={(e) =>
                              setEditForm({
                                ...editForm,
                                email: e.target.value,
                              })
                            }
                          />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <button
                    onClick={() => {
                      axios
                        .put(
                          "http://127.0.0.1:8000/api/auth/user/profile/",
                          editForm,
                          {
                            headers: {
                              Authorization: `Bearer ${localStorage.getItem(
                                "token"
                              )}`,
                            },
                          }
                        )
                        .then(() => {
                          setUserInfo({ ...userInfo, ...editForm });
                          setEditMode(false);
                        })
                        .catch((err) => {
                          console.error("Failed to update profile", err);
                          alert("Failed to update profile.");
                        });
                    }}
                  >
                    Save
                  </button>
                  <button onClick={() => setEditMode(false)}>Cancel</button>
                </div>
              )}
            </>
          ) : (
            <p>Loading user info...</p>
          )}
        </div>

        {/* Right Side (Report History) */}
        <div className="profile-right">
          <div className="profile-models-header">
            <h2>Report History</h2>
            <div className="profile-actions">
              <div className="profile-search">
                <FaSearch className="profile-search-icon" />
                <input
                  type="text"
                  placeholder="Search reports..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {/* Profile Dropdown */}
              <div className="profile-dropdown" ref={dropdownRef}>
                <button
                  className="profile-dropdown-btn"
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                >
                  <FaUserCircle className="profile-dropdown-icon" />
                </button>
                {dropdownOpen && (
                  <div className="profile-dropdown-menu">
                    <Link to="/profile" className="profile-dropdown-item">
                      <FaUser className="dropdown-icon" /> Your Profile
                    </Link>
                    <button
                      className="profile-dropdown-item"
                      onClick={() => {
                        setEditMode(true);
                        setDropdownOpen(false);
                        setEditForm({
                          name: userInfo?.name || "",
                          surname: userInfo?.surname || "",
                          email: userInfo?.email || "",
                        });
                      }}
                    >
                      <FaEdit className="dropdown-icon" /> Edit Profile
                    </button>
                    <button
                      className="profile-dropdown-item logout-btn"
                      onClick={handleLogout}
                    >
                      <FaSignOutAlt className="dropdown-icon" /> Log Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Divider Above Report List */}
          <hr className="profile-divider first-divider" />

          <div className="profile-models-list">
            {filteredReports.length > 0 ? (
              filteredReports.map((report) => (
                <div key={report.id} className="profile-model">
                  <div className="profile-model-info">
                    <h3 className="profile-model-name">{report.name}</h3>
                    <p>{report.content}</p>
                    <small>
                      {new Date(report.creation_date).toLocaleString()}
                    </small>
                  </div>
                  <hr className="profile-divider" />
                </div>
              ))
            ) : (
              <p className="profile-no-models">No reports found.</p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Profile;
