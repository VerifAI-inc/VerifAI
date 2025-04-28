// src/pages/Tables.js

import React, { useState, useEffect } from "react";
import "../styles/pages/Tables.css";
import { Link, useNavigate } from "react-router-dom";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

const epsilons = ["0.0", "0.1", "1.0", "5.0", "10.0"];

const Tables = () => {
  const [allResults, setAllResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/api/store-results/")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch results");
        return response.json();
      })
      .then((data) => {
        console.log("✅ Results fetched for tables:", data);
        setAllResults(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("❌ Error fetching results:", error);
        setLoading(false);
      });
  }, []);

  const downloadTable = (tableData, tableName) => {
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(tableData);
    XLSX.utils.book_append_sheet(wb, ws, tableName);
    const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const data = new Blob([excelBuffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    saveAs(data, `${tableName}.xlsx`);
  };

  const getFairnessTable = (epsilon) => {
    const res = allResults?.[epsilon];
    if (!res || !res.fairness) return [];

    const fairnessTables = [];

    const fairnessOrig = epsilon === "0.0" ? res.fairness.orig_without_dp : res.fairness.orig_with_dp;
    const fairnessMitigator = epsilon === "0.0" ? res.fairness.mitigator_without_dp : res.fairness.mitigator_with_dp;

    if (!fairnessOrig || !fairnessMitigator) return [];

    const metrics = Object.keys(fairnessOrig);

    metrics.forEach(metric => {
      fairnessTables.push(["Original", metric, fairnessOrig[metric]]);
      fairnessTables.push(["Mitigator", metric, fairnessMitigator[metric]]);
    });

    return fairnessTables;
  };

  const getPrivacyTable = (epsilon) => {
    const res = allResults?.[epsilon];
    if (!res || !res.privacy) return [];

    const privacyOrig = epsilon === "0.0" ? res.privacy.orig_without_dp : res.privacy.orig_with_dp;
    const privacyMitigator = epsilon === "0.0" ? res.privacy.mitigator_without_dp : res.privacy.mitigator_with_dp;

    if (!privacyOrig || !privacyMitigator) return [];

    const groups = ["g0-", "g0+", "g1-", "g1+"];

    const privacyTables = groups.map(group => ([
      "Original", group, privacyOrig[group] || "-"
    ])).concat(groups.map(group => ([
      "Mitigator", group, privacyMitigator[group] || "-"
    ])));

    return privacyTables;
  };

  const getAccuracyTable = (epsilon) => {
    const res = allResults?.[epsilon];
    if (!res || !res.accuracy) return [];

    const acc = res.accuracy;

    return [
      ["Total Train Accuracy", acc.total_train_acc || "-"],
      ["Total Test Accuracy", acc.total_test_acc || "-"],
      ["Test g0-", acc.test_acc_g0_minus || "-"],
      ["Test g0+", acc.test_acc_g0_plus || "-"],
      ["Test g1-", acc.test_acc_g1_minus || "-"],
      ["Test g1+", acc.test_acc_g1_plus || "-"]
    ];
  };

  const epsilonLabel = (eps) => eps === "0.0" ? "Without DP" : `With DP (ε=${eps})`;

  return (
    <div className="tables-page">
      {/* Header */}
      <section className="tables-header">
        <div className="container-tables">
          <h2>VERIFAI</h2>
          <div className="page-tab-tables">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>TABLES</span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="tables-section">
        <h1 className="tables-title">Results Tables</h1>
        <p className="tables-description">Tables below summarize the results for different ε (epsilon) values.</p>

        {loading ? (
          <p className="no-tables-message">Loading results...</p>
        ) : (
          epsilons.map((eps) => (
            <div key={eps} className="tables-content">
              <h2 style={{ marginBottom: "10px" }}>{epsilonLabel(eps)}</h2>

              {/* Fairness Table */}
              <div className="table-wrapper">
                <div className="table-header">
                  <h3>Fairness Metrics</h3>
                  <button
                    className="tables-download-btn"
                    onClick={() => downloadTable([["Model", "Metric", "Value"], ...getFairnessTable(eps)], `Fairness_Metrics_eps${eps}`)}
                  >
                    <FaDownload />
                  </button>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Metric</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getFairnessTable(eps).map((row, idx) => (
                      <tr key={idx}>
                        {row.map((cell, i) => (
                          <td key={i}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Privacy Table */}
              <div className="table-wrapper">
                <div className="table-header">
                  <h3>Privacy Risks</h3>
                  <button
                    className="tables-download-btn"
                    onClick={() => downloadTable([["Model", "Group", "Privacy Risk"], ...getPrivacyTable(eps)], `Privacy_Risks_eps${eps}`)}
                  >
                    <FaDownload />
                  </button>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Group</th>
                      <th>Privacy Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getPrivacyTable(eps).map((row, idx) => (
                      <tr key={idx}>
                        {row.map((cell, i) => (
                          <td key={i}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Accuracy Table */}
              <div className="table-wrapper">
                <div className="table-header">
                  <h3>Train-Test Accuracies</h3>
                  <button
                    className="tables-download-btn"
                    onClick={() => downloadTable([["Metric", "Value"], ...getAccuracyTable(eps)], `Accuracies_eps${eps}`)}
                  >
                    <FaDownload />
                  </button>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {getAccuracyTable(eps).map((row, idx) => (
                      <tr key={idx}>
                        {row.map((cell, i) => (
                          <td key={i}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          ))
        )}

        <div className="tables-buttons-container">
          <button className="tables-back-btn" onClick={() => navigate("/upload")}> <FaArrowLeft className="tables-back-arrow" /> Back to Upload</button>
        </div>
      </section>
    </div>
  );
};

export default Tables;
