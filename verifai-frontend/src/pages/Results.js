import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaDownload, FaArrowRight, FaArrowLeft } from "react-icons/fa";
import Slider from "../components/Slider";
import API_BASE_URL from "../config";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "../styles/Global.css";
import "../styles/pages/Results.css";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { useRef } from "react";

const epsilonsNeeded = ["0.1", "1", "5", "10"];

const Results = () => {
  const navigate = useNavigate();
  const [epsilon, setEpsilon] = useState(1.0);
  const [allResults, setAllResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPopup, setShowPopup] = useState(true);

  const graphContainerRef = useRef(null); 

  const handleDownloadResults = async () => {
    if (!graphContainerRef.current) {
      console.error("Graph container not found!");
      return;
    }

    const canvas = await html2canvas(graphContainerRef.current, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");
    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

    pdf.addImage(imgData, "PNG", 0, 20, pdfWidth, pdfHeight);
    pdf.save("VerifAI_Results.pdf");
  };

  useEffect(() => {
    const interval = setInterval(() => {
      fetch(`${API_BASE_URL}/api/store-results/`)
        .then((response) => {
          if (!response.ok) throw new Error("Failed to fetch results");
          return response.json();
        })
        .then((data) => {
          console.log("Results from backend:", data);
          setAllResults(data);

          const allAvailable = epsilonsNeeded.every((eps) => {
            const res = data[eps];
            return res && res.privacy && res.fairness && res.accuracy;
          });

          if (allAvailable) {
            clearInterval(interval);
            setLoading(false);
          }
        })
        .catch((error) => {
          console.error("Error fetching results:", error);
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

  const getWithoutDpResults = () => {
    if (!allResults) return null;
    return allResults["0.0"] || null;
  };

  const subpopLabels = {
    "g0-": "Unprivileged Unfavorable",
    "g0+": "Unprivileged Favorable",
    "g1-": "Privileged Unfavorable",
    "g1+": "Privileged Favorable",
  };

  const fairnessMetricsLabels = {
    bal_acc: "Bal Acc",
    avg_odds_diff: "Avg Odds Diff",
    disp_imp: "Disp Imp",
    stat_par_diff: "Stat Par Diff",
    eq_opp_diff: "Eq Opp Diff",
    theil_ind: "Theil Ind",
  };

  const getPrivacyGraphData = (withDp) => {
    const results = withDp ? getCurrentResults() : getWithoutDpResults();
    if (!results || !results.privacy) return [];

    const orig = withDp
      ? results.privacy?.orig_with_dp || {}
      : results.privacy?.orig_without_dp || {};
    const mitigator = withDp
      ? results.privacy?.mitigator_with_dp || {}
      : results.privacy?.mitigator_without_dp || {};

    return Object.entries(subpopLabels).map(([key, label]) => ({
      subpopulation: label,
      Orig: orig[key],
      Mitigator: mitigator[key],
    }));
  };

  const getFairnessGraphData = (withDp) => {
    const results = withDp ? getCurrentResults() : getWithoutDpResults();
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
          fairnessData[metricKey] = {
            metric: fairnessMetricsLabels[metricKey],
          };
        }
        fairnessData[metricKey][label] = value;
      }
    }

    return Object.values(fairnessData);
  };

  const getMaxPrivacyRisk = () => {
    const results = getCurrentResults();
    const withoutDpResults = getWithoutDpResults();
    if (!results || !withoutDpResults) return 1;

    const values = [];
    const fields = [
      "orig_without_dp",
      "mitigator_without_dp",
      "orig_with_dp",
      "mitigator_with_dp",
    ];

    fields.forEach((field) => {
      const data =
        results.privacy[field] || withoutDpResults.privacy[field] || {};
      ["g0-", "g0+", "g1-", "g1+"].forEach((key) => {
        if (data[key] !== undefined) {
          values.push(data[key]);
        }
      });
    });

    if (values.length === 0) return 1;
    return Math.ceil(Math.max(...values) * 20) / 20;
  };

  const renderGraphs = (withDp) => {
    const results = withDp ? getCurrentResults() : getWithoutDpResults();
    if (!results) return null;

    return (
      <div className="graph-card">
        {/* Privacy Risk Graph */}
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={getPrivacyGraphData(withDp)}
            margin={{ top: 20, right: 30, left: 50, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="subpopulation"
              angle={-20}
              textAnchor="end"
              interval={0}
              height={80}
            />
            <YAxis domain={[0, getMaxPrivacyRisk()]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Orig" fill="#8884d8" barSize={20} />
            <Bar dataKey="Mitigator" fill="#82ca9d" barSize={20} />
          </BarChart>
        </ResponsiveContainer>
        <p
          style={{
            textAlign: "center",
            marginTop: "4px",
            fontSize: "13px",
            opacity: 0.8,
          }}
        >
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
            <XAxis
              dataKey="metric"
              angle={-20}
              textAnchor="end"
              interval={0}
              height={80}
            />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Original" fill="#ffa07a" barSize={20} />
            <Bar dataKey="Mitigator" fill="#0000FF" barSize={20} />
          </BarChart>
        </ResponsiveContainer>
        <p
          style={{
            textAlign: "center",
            marginTop: "4px",
            fontSize: "13px",
            opacity: 0.8,
          }}
        >
          Fairness Metrics Comparison
        </p>
      </div>
    );
  };

  return (
    <div className="results-container">
      {showPopup && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-btn" onClick={() => setShowPopup(false)}>
              &times;
            </button>
            <h3>Servers Currently Unavailable</h3>
            <p>
              We're performing system updates. Interested in investing in VerifAI?
              Visit our homepage to learn more.
            </p>
            <button className="modal-home-btn" onClick={() => navigate("/")}>Go to Homepage</button>
          </div>
        </div>
      )}
      <section className="page-title-home">
        <div className="container-home">
          {/* <h2>VerifAI</h2> */}
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>RESULTS</span>
          </div>
        </div>
      </section>

      <div className="results-main-content">
        {/* Action Buttons */}
        <div
          className="results-action-group"
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "30px",
            marginTop: "30px",
          }}
        >
          <Link
            to="/upload"
            className="results-btn"
            style={{ width: "250px", textDecoration: "none" }}
            disabled={loading}
          >
            <FaArrowLeft className="icon-space" /> Back to Upload
          </Link>
          <button
            className="results-btn"
            style={{ width: "250px" }}
            onClick={handleDownloadResults}
            disabled={loading}
          >
            <FaDownload className="icon-space" /> Download Results
          </button>
        </div>

        {/* Header */}
        <div className="results-header">
          <h1 className="results-title">Results Analysis</h1>
          <p className="results-description">
            Select one of the following ε (epsilon) values:{" "}
            <strong>0.1, 1, 5, 10</strong>
          </p>
        </div>

        {/* Slider */}
        <div className="slider-container">
          <Slider
            value={epsilon}
            onChange={handleSliderChange}
            label="Epsilon (ε)"
          />
        </div>

        {/* Graphs */}
        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p className="loading-text">Crunching numbers... Please wait ⏳</p>
          </div>
        ) : (
          <div className="results-graphs-wrapper">
            <div ref={graphContainerRef} className="graphs-container">
              <div style={{ width: "48%" }}>
                <h2 style={{ textAlign: "center", marginBottom: "10px" }}>
                  Without DP
                </h2>
                {renderGraphs(false)}
              </div>
              <div style={{ width: "48%" }}>
                <h2 style={{ textAlign: "center", marginBottom: "10px" }}>
                  With DP
                </h2>
                {renderGraphs(true)}
              </div>
            </div>
          </div>
        )}

        {/* Tables and Report Buttons */}
        <div className="results-button-group">
          <button
            className="results-btn"
            style={{ width: "250px" }}
            onClick={() => navigate("/tables")}
            disabled={loading}
          >
            See Tables <FaArrowRight />
          </button>
          <button
            className="results-btn"
            style={{ width: "250px" }}
            onClick={() => navigate("/reports")}
            disabled={loading}
          >
            See Report <FaArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;
