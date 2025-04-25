// Results.js
import React, { useState, useEffect } from "react";
import Slider from "../components/Slider";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import "../styles/Global.css";
import "../styles/pages/Results.css";

const Results = () => {
  const [epsilon, setEpsilon] = useState(1.0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

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
        setLoading(false);
      });
  }, []);

  const handleSliderChange = (event) => {
    setEpsilon(event.target.value);
  };

  const subpopLabels = {
    "g0-": "Unprivileged Unfavorable",
    "g0+": "Unprivileged Favorable",
    "g1-": "Privileged Unfavorable",
    "g1+": "Privileged Favorable",
  };

  const getGraphData = (withDp) => {
    if (!results || !results.privacy) return [];

    const orig = withDp ? results.privacy?.orig_with_dp || {} : results.privacy?.orig_without_dp || {};
    const mitigator = withDp ? results.privacy?.mitigator_with_dp || {} : results.privacy?.mitigator_without_dp || {};

    return Object.entries(subpopLabels).map(([key, label]) => ({
      subpopulation: label,
      Orig: orig[key],
      Mitigator: mitigator[key],
    }));
  };

  const getMaxPrivacyRisk = () => {
    if (!results || !results.privacy) return 1;

    const values = [];
    const all_keys = ["g0-", "g0+", "g1-", "g1+"];
    const fields = [
      "orig_without_dp", "mitigator_without_dp",
      "orig_with_dp", "mitigator_with_dp",
    ];

    fields.forEach((field) => {
      const data = results.privacy[field] || {};
      all_keys.forEach((key) => {
        if (data[key] !== undefined) {
          values.push(data[key]);
        }
      });
    });

    if (values.length === 0) return 1;
    const maxVal = Math.max(...values);
    const roundedMax = Math.ceil(maxVal * 20) / 20;
    return roundedMax;
  };

  const renderGraph = (title, withDp) => (
    <div className="graph-card">
      <h2>{title}</h2>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart
          data={getGraphData(withDp)}
          margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="subpopulation" angle={-20} textAnchor="end" interval={0} height={100} />
          <YAxis domain={[0, getMaxPrivacyRisk()]} />
          <Tooltip />
          <Legend />
          <Bar dataKey="Orig" fill="#8884d8" barSize={20} />
          <Bar dataKey="Mitigator" fill="#82ca9d" barSize={20} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

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
        <div className="results-graphs-wrapper">
          <div className="graphs-container">
            {renderGraph("Privacy Risk (Without DP)", false)}
            {renderGraph("Privacy Risk (With DP)", true)}
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