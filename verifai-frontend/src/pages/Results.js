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

  const getGraphData = () => {
    if (!results || !results.privacy) return [];

    const subpopLabels = {
      "g0-": "Unprivileged Unfavorable",
      "g0+": "Unprivileged Favorable",
      "g1-": "Privileged Unfavorable",
      "g1+": "Privileged Favorable",
    };

    return Object.entries(subpopLabels).map(([key, label]) => ({
      subpopulation: label,
      Orig: results.privacy[key],
      // If you later add mitigator values, you can extend here
      // Mitigator: results.mitigator_privacy?.[key] || null,
    }));
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
            <h2>Privacy Risk Across Subpopulations</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={getGraphData()}
                margin={{ top: 30, right: 30, left: 20, bottom: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="subpopulation" angle={-15} textAnchor="end" interval={0} height={80} />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Orig" fill="#8884d8" barSize={40} />
              </BarChart>
            </ResponsiveContainer>
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