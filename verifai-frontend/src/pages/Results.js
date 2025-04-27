import React, { useState, useEffect } from "react";
import Slider from "../components/Slider";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import "../styles/Global.css";
import "../styles/pages/Results.css";

const Results = () => {
  const [epsilon, setEpsilon] = useState(1.0);
  const [allResults, setAllResults] = useState(null);
  const [loading, setLoading] = useState(true);

  const epsilonsNeeded = ["0.1", "1", "5", "10"];

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:8000/api/store-results/")
        .then((response) => {
          if (!response.ok) throw new Error("Failed to fetch results");
          return response.json();
        })
        .then((data) => {
          console.log("✅ Polling results:", data);
          setAllResults(data);

          const allAvailable = epsilonsNeeded.every((eps) => {
            const res = data[eps];
            return res &&
              res.privacy && Object.keys(res.privacy).length > 0 &&
              res.fairness && Object.keys(res.fairness).length > 0 &&
              res.accuracy && Object.keys(res.accuracy).length > 0;
          });

          if (allAvailable) {
            clearInterval(interval); // stop polling
            setLoading(false);
          }
        })
        .catch((error) => {
          console.error("❌ Error polling results:", error);
        });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleSliderChange = (event) => {
    setEpsilon(parseFloat(event.target.value));
  };

  const getCurrentResults = () => {
    if (!allResults) return null;
    return allResults[String(epsilon)] || null;
  };

  const subpopLabels = {
    "g0-": "UU",
    "g0+": "UF",
    "g1-": "PU",
    "g1+": "PF",
  };

  const fairnessMetricsLabels = {
    bal_acc: "Bal Acc",
    avg_odds_diff: "Avg Odds Diff",
    disp_imp: "Disp Imp",
    stat_par_diff: "Stat Par Diff",
    eq_opp_diff: "Eq Opp Diff",
    theil_ind: "Theil Ind",
  };

  const getGraphData = (withDp) => {
    const results = getCurrentResults();
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
    const results = getCurrentResults();
    if (!results || !results.privacy) return 1;

    const values = [];
    const fields = ["orig_without_dp", "mitigator_without_dp", "orig_with_dp", "mitigator_with_dp"];
    const all_keys = ["g0-", "g0+", "g1-", "g1+"];

    fields.forEach((field) => {
      const data = results.privacy[field] || {};
      all_keys.forEach((key) => {
        if (data[key] !== undefined) {
          values.push(data[key]);
        }
      });
    });

    if (values.length === 0) return 1;
    return Math.ceil(Math.max(...values) * 20) / 20;
  };

  const getFairnessGraphData = (withDp) => {
    const results = getCurrentResults();
    if (!results || !results.fairness) return [];

    const entries = Object.entries(results.fairness);
    const relevantEntries = entries.filter(([key, _]) =>
      withDp ? key.endsWith("_with_dp") : key.endsWith("_without_dp")
    );

    const fairnessData = {};

    for (const [name, metrics] of relevantEntries) {
      const label = name.startsWith("orig") ? "Original" : "Mitigator";
      for (const [metricKey, value] of Object.entries(metrics)) {
        if (!fairnessData[metricKey]) {
          fairnessData[metricKey] = { metric: fairnessMetricsLabels[metricKey] };
        }
        fairnessData[metricKey][label] = value;
      }
    }

    return Object.values(fairnessData);
  };

  const renderGraphs = (withDp) => (
    <div className="graph-card">
      {/* Privacy Risk Graph */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={getGraphData(withDp)}
          margin={{ top: 20, right: 30, left: 50, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="subpopulation" angle={-20} textAnchor="end" interval={0} height={80} />
          <YAxis domain={[0, getMaxPrivacyRisk()]} />
          <Tooltip />
          <Legend />
          <Bar dataKey="Orig" fill="#8884d8" barSize={20} />
          <Bar dataKey="Mitigator" fill="#82ca9d" barSize={20} />
        </BarChart>
      </ResponsiveContainer>
      <p style={{ textAlign: "center", marginTop: "4px", fontSize: "13px", opacity: 0.8 }}>
        Privacy Risk across Subpopulations
      </p>

      <div style={{ marginTop: "30px" }}></div>

      {/* Fairness Metrics Graph */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={getFairnessGraphData(withDp)}
          margin={{ top: 20, right: 30, left: 50, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" angle={-20} textAnchor="end" interval={0} height={80} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Original" fill="#ffa07a" barSize={20} />
          <Bar dataKey="Mitigator" fill="#0000FF" barSize={20} />
        </BarChart>
      </ResponsiveContainer>
      <p style={{ textAlign: "center", marginTop: "4px", fontSize: "13px", opacity: 0.8 }}>
        Fairness Metrics Comparison
      </p>
    </div>
  );

  return (
    <div className="other-pages">
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
            <strong>ε:</strong> 0.1, 1, 5, 10 &nbsp;|&nbsp;
            <strong>UU:</strong> Unprivileged Unfavorable &nbsp;|&nbsp;
            <strong>UF:</strong> Unprivileged Favorable &nbsp;|&nbsp;
            <strong>PU:</strong> Privileged Unfavorable &nbsp;|&nbsp;
            <strong>PF:</strong> Privileged Favorable
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
              <div style={{ width: "48%" }}>
                <h2 style={{ textAlign: "center", marginBottom: "10px" }}>Without DP</h2>
                {renderGraphs(false)}
              </div>

              <div style={{ width: "48%" }}>
                <h2 style={{ textAlign: "center", marginBottom: "10px" }}>With DP</h2>
                {renderGraphs(true)}
              </div>
            </div>
          </div>
        )}

        <div className="results-buttons">
          <button className="btn" disabled={loading}>See Tables</button>
          <button className="btn" disabled={loading}>See Report</button>
        </div>
      </div>
    </div>
  );
};

export default Results;