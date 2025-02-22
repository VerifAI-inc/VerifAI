import React, { useState } from "react";
import "../styles/Reports.css";
import { FaDownload } from "react-icons/fa";

const Reports = () => {
  const [reportUrl, setReportUrl] = useState(null); 

  const handleGenerateReport = () => {
    console.log("Generating Report...");
    alert("Report generation started!");

    // Simulating backend response with a dummy PDF file
    setTimeout(() => {
      setReportUrl("https://www.orimi.com/pdf-test.pdf"); // Replace with backend response URL
    }, 2000);
  };

  const handleDownloadReport = () => {
    if (reportUrl) {
      window.open(reportUrl, "_blank");
    } else {
      alert("No report available. Please generate one first.");
    }
  };

  return (
    <div className="reports-page">
      <div className="reports-container">
        {/* Header Section */}
        <div className="reports-header">
          <h1>Generate Report</h1>
          <button className="download-btn" onClick={handleDownloadReport}>
            <FaDownload size={24} />
          </button>
        </div>

        {/* Report Generation Section */}
        <div className="report-section">
          <p className="report-description">
            Click the button below to generate a new report. Once generated, the report will appear below, and you can download it.
          </p>
          <button className="generate-btn" onClick={handleGenerateReport}>
            Generate Report
          </button>
        </div>

        {/* Report Display Area */}
        <div className="report-content">
          {reportUrl ? (
            <iframe 
              src={reportUrl} 
              title="Generated Report" 
              className="pdf-viewer" 
            ></iframe>
          ) : (
            <p className="report-placeholder">No report available. Generate a report to view it here.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;