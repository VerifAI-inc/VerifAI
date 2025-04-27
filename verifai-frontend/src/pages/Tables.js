import React, { useState } from "react";
import "../styles/pages/Tables.css";
import { Link, useNavigate } from "react-router-dom";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

const Tables = () => {
  const [tablesGenerated, setTablesGenerated] = useState(false);
  const navigate = useNavigate();

  const handleGenerateTables = () => {
    setTablesGenerated(true);
  };

  const downloadTable = (tableData, tableName) => {
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(tableData);
    XLSX.utils.book_append_sheet(wb, ws, tableName);
    const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const data = new Blob([excelBuffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    saveAs(data, `${tableName}.xlsx`);
  };

  // Dummy Data for Tables
  const fairnessMetrics = [
    ["orig", "bal_acc", "0.837", "0.015"],
    ["orig", "avg_odds_diff", "0.161", "0.039"],
    ["orig", "disp_imp", "0.566", "0.032"],
  ];

  const privacyRiskMetrics = [
    ["orig", "entire_dataset_mia_privacy_risk", "0.522", "0.003"],
    ["transf", "subpopulation_0_0", "0.546", "0.021"],
    ["orig", "subpopulation_1_0", "0.601", "0.016"],
  ];

  const trainTestAccuracies = [
    ["0.810", "0.809", "0.796", "0.802", "0.802"],
    ["0.705", "0.706", "0.718", "0.721", "0.715"],
    ["0.856", "0.858", "0.787", "0.850", "0.804"],
  ];

  return (
    <div className="tables-page">
      {/* Background Header */}
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

      {/* Tables Section */}
      <section className="tables-section">
        <h1 className="tables-title">Generate Tables</h1>
        <p className="tables-description">
          Click the button below to generate new tables. Once generated, they will appear below, and you can download them.
        </p>
        
        {/* Buttons Section */}
        <div className="tables-buttons-container">
          <button className="tables-generate-btn" onClick={handleGenerateTables}>
            Generate Tables
          </button>
          <button className="tables-back-btn" onClick={() => navigate("/upload")}>
            <FaArrowLeft className="tables-back-arrow" /> Back to Upload
          </button>
        </div>

        {/* Tables Display Area */}
        {tablesGenerated ? (
          <div className="tables-content">
            {/* Fairness Metrics Table */}
            <div className="table-wrapper">
              <div className="table-header">
                <h2>Fairness Metrics Table</h2>
                <button className="tables-download-btn" onClick={() => downloadTable([["Method", "Metric", "Mean", "Error"], ...fairnessMetrics], "Fairness_Metrics")}>
                  <FaDownload />
                </button>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Method</th>
                    <th>Metric</th>
                    <th>Mean</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {fairnessMetrics.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, i) => (
                        <td key={i}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* MIA Privacy Risks Metrics Table */}
            <div className="table-wrapper">
              <div className="table-header">
                <h2>MIA Privacy Risks Metrics Table</h2>
                <button className="tables-download-btn" onClick={() => downloadTable([["Method", "Metric", "Mean Privacy Risk", "Error"], ...privacyRiskMetrics], "MIA_Privacy_Risks")}>
                  <FaDownload />
                </button>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Method</th>
                    <th>Metric</th>
                    <th>Mean Privacy Risk</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {privacyRiskMetrics.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, i) => (
                        <td key={i}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Train-Test Accuracies Table */}
            <div className="table-wrapper">
              <div className="table-header">
                <h2>Train-Test Accuracies Table</h2>
                <button className="tables-download-btn" onClick={() => downloadTable([["orig_acc_mean", "transf_acc_mean", "reweigh_acc_mean", "dir_acc_mean", "eg_acc_mean"], ...trainTestAccuracies], "Train_Test_Accuracies")}>
                  <FaDownload />
                </button>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>orig_acc_mean</th>
                    <th>transf_acc_mean</th>
                    <th>reweigh_acc_mean</th>
                    <th>dir_acc_mean</th>
                    <th>eg_acc_mean</th>
                  </tr>
                </thead>
                <tbody>
                  {trainTestAccuracies.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, i) => (
                        <td key={i}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <p className="no-tables-message">No tables available. Generate tables to view them here.</p>
        )}
      </section>
    </div>
  );
};

export default Tables;
