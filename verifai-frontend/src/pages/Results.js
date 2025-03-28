import React, { useState } from "react";
import Slider from "../components/Slider";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import "../styles/Global.css";
import "../styles/pages/Results.css";
import example1 from "../assets/graphs/example1.png";
import example2 from "../assets/graphs/example2.png";
import { Link } from "react-router-dom";

const Results = () => {
  const [epsilon, setEpsilon] = useState(1.0);

  const handleSliderChange = (event) => {
    setEpsilon(event.target.value);
  };

  return (
    <div className="results-container">
      <div className="results-actions">
        <Link to="/upload" className="btn back-btn">
          <FaArrowLeft className="icon-space" />
          Back to Upload
        </Link>

        <button className="download-btn">
          <FaDownload className="icon-space" />
          Download Graphs
        </button>
      </div>

      {/* Title & Description */}
      <div className="results-header">
        <h1 className="results-title">Results Analysis</h1>
        <p className="results-description">
          Select one of the following ε (epsilon) values: <strong>0.1, 1, 5, 10</strong>
        </p>
      </div>

      {/* Slider */}
      <div className="slider-container">
        <Slider value={epsilon} onChange={handleSliderChange} label="Epsilon (ε)" />
      </div>

      {/* Graphs Section */}
      <div className="graphs-container">
        <div className="graph-card">
          <h2>Without DP</h2>
          {/* Graphs will be placed here */}
          <img src={example1} alt="" />
          <img src={example2} alt="" />
        </div>

        <div className="graph-card">
          <h2>With DP</h2>
          {/* Graphs will be placed here */}
        </div>
      </div>

      {/* Buttons for Tables and Reports */}
      <div className="results-buttons">
        <button className="btn">See Tables</button>
        <button className="btn">See Report</button>
      </div>
    </div>
  );
};

export default Results;