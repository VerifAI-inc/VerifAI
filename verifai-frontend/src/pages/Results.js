import React, { useState, useEffect } from "react";
import Slider from "../components/Slider";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import "../styles/Global.css";
import "../styles/pages/Results.css";
import { Link } from "react-router-dom";

const Results = () => {
  const [epsilon, setEpsilon] = useState(1.0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true); // ✅ loading state

  useEffect(() => {
    fetch("http://localhost:8000/api/store-results/")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch results");
        return response.json();
      })
      .then((data) => {
        console.log("✅ Results from backend:", data);
        setResults(data);
      })
      .catch((error) => {
        console.error("❌ Error fetching results:", error);
      })
      .finally(() => {
        setLoading(false); // ✅ hide spinner
      });
  }, []);

  const handleSliderChange = (event) => {
    setEpsilon(event.target.value);
  };

  return (
    <div className="results-container">
      <div className="results-actions">
        <Link to="/upload" className="btn back-btn" disabled={loading}>
          <FaArrowLeft className="icon-space" />
          Back to Upload
        </Link>
        <button className="download-btn" disabled={loading}>
          <FaDownload className="icon-space" />
          Download Results
        </button>
      </div>

      <div className="results-header">
        <h1 className="results-title">Results Analysis</h1>
        <p className="results-description">
          Select one of the following ε (epsilon) values: <strong>0.1, 1, 5, 10</strong>
        </p>
      </div>

      <div className="slider-container">
        <Slider value={epsilon} onChange={handleSliderChange} label="Epsilon (ε)" />
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text">Crunching numbers... Please wait ⏳</p>
        </div>
      ) : (
        <div className="graphs-container">
          <div className="graph-card">
            <h2>Without DP</h2>
            <div className="results-data">
              <p>Test Accuracy: {results.accuracy.without_dp.test}</p>
              <p>Train Accuracy: {results.accuracy.without_dp.train}</p>
              {Object.entries(results.accuracy.without_dp.subgroups).map(([key, val]) => (
                <p key={key}>{key} Subgroup Accuracy: {val}</p>
              ))}
            </div>
          </div>

          <div className="graph-card">
            <h2>With DP</h2>
            <div className="results-data">
              <p>Test Accuracy: {results.accuracy.with_dp.test}</p>
              <p>Train Accuracy: {results.accuracy.with_dp.train}</p>
              {Object.entries(results.accuracy.with_dp.subgroups).map(([key, val]) => (
                <p key={key}>{key} Subgroup Accuracy: {val}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="results-buttons">
        <button className="btn" disabled={loading}>See Tables</button>
        <button className="btn" disabled={loading}>See Report</button>
      </div>
    </div>
  );
};

export default Results;