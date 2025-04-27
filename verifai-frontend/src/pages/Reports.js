import React, { useState } from "react";
import "../styles/pages/Reports.css";
import { Link, useNavigate } from "react-router-dom";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import jsPDF from "jspdf";

const Reports = () => {
  const [reportText, setReportText] = useState(null);
  const navigate = useNavigate();

  // Generate Sample Report Text
  const handleGenerateReport = () => {
    console.log("Generating Report...");
    
    setTimeout(() => {
      setReportText("VerifAI Report:\n\nAI fairness analysis completed successfully. Bias detected in dataset, mitigation strategies suggested. Privacy metrics are within acceptable limits.");
    }, 2000);
  };

  // Download Report as PDF
  const handleDownloadReport = () => {
    if (reportText) {
      const doc = new jsPDF();
      doc.text(reportText, 10, 10);
      doc.save("VerifAI_Report.pdf");
    } else {
      alert("No report available. Please generate one first.");
    }
  };

  return (
    <div className="reports-page">
      {/* Background Header (Same as Home Page) */}
      <section className="reports-header">
        <div className="container-reports">
          <h2>VERIFAI</h2>
          <div className="page-tab-reports">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>REPORTS</span>
          </div>
        </div>
      </section>

      {/* Reports Section */}
      <section className="reports-section">
        <h1 className="reports-title">Generate Report</h1>
        <p className="reports-description">
          Click the button below to generate a new report. Once generated, you can download it as a PDF or go back to the upload page.
        </p>

        <div className="reports-button-container">
          <button className="reports-generate-btn" onClick={handleGenerateReport}>
            Generate Report
          </button>
          <button className="reports-download-btn" onClick={handleDownloadReport}>
            <FaDownload /> Download PDF
          </button>
          <button className="reports-back-btn" onClick={() => navigate("/upload")}>
            <FaArrowLeft /> Back to Upload
          </button>
        </div>

        {/* Report Display */}
        <div className="report-content">
          {reportText ? (
            <p className="generated-report">{reportText}</p>
          ) : (
            <p className="report-placeholder">No report available. Generate a report to view it here.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default Reports;
