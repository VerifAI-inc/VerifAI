// src/pages/Reports.js

import React, { useState } from "react";
import "../styles/pages/Reports.css";
import { Link, useNavigate } from "react-router-dom";
import { FaDownload, FaArrowLeft } from "react-icons/fa";
import jsPDF from "jspdf";

const Reports = () => {
  const [reportText, setReportText] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Fetch results from backend
  const fetchResults = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/store-results/");
      const data = await response.json();
      if (!data) return null;
      const resultsNoDP = data["0.0"];
      if (!resultsNoDP) return null;

      return {
        accuracy: resultsNoDP.accuracy?.without_dp || {},
        fairness_metrics: resultsNoDP.fairness?.orig_without_dp || {},
        privacy_metrics: resultsNoDP.privacy?.orig_without_dp || {},
      };
    } catch (error) {
      console.error("Error fetching results:", error);
      return null;
    }
  };

  const buildPrompt = (results) => {
    const fairnessMetrics = JSON.stringify(results.fairness_metrics, null, 2);
    const privacyMetrics = JSON.stringify(results.privacy_metrics, null, 2);
    const subpopAccuracies = JSON.stringify(results.accuracy.subgroups, null, 2);
    return `You are an expert AI evaluation assistant.

Given the following AI model evaluation results, please generate a detailed, structured report with sections for Summary, Fairness Analysis, Privacy Analysis, Utility Analysis, Risks Identified, and Recommendations.

Model Evaluation Results:
- Overall Accuracy: ${results.accuracy.test}%
- Fairness Metrics: ${fairnessMetrics}
- Privacy Metrics: ${privacyMetrics}
- Subpopulation Accuracies: ${subpopAccuracies}`;
  };

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const fetchedResults = await fetchResults();
      if (!fetchedResults) throw new Error("No results");

      const prompt = buildPrompt(fetchedResults);
      const completionResponse = await fetch("http://localhost:8000/api/generate-report/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!completionResponse.ok) throw new Error("Failed report generation");

      const completionData = await completionResponse.json();
      setReportText(typeof completionData.report_text === "string" ? completionData.report_text : completionData.report_text);
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Error generating report.");
    }
    setLoading(false);
  };

  const handleDownloadReport = () => {
    if (!reportText) {
      alert("No report available.");
      return;
    }
  
    const doc = new jsPDF();
    const marginLeft = 10;
    const marginRight = 10;
    const maxWidth = 180; // 210 (A4 width) - 2*15 margins
  
    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("VerifAI Evaluation Report", marginLeft, 20);
  
    let y = 30; // vertical starting position
    const lineSpacing = 8;
  
    const cleanedText = cleanUpReportText(reportText);
    const lines = cleanedText.split("\n");
  
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
  
    lines.forEach((line) => {
      if (y > 270) {  // Page end check
        doc.addPage();
        y = 20;
      }
  
      if (line.startsWith("##")) {
        const heading = line.replace(/^##\s*/, "");
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text(heading, marginLeft, y);
        y += lineSpacing + 2;
        doc.setFontSize(12);
        doc.setFont("helvetica", "normal");
      } else if (line.trim() === "") {
        y += lineSpacing / 2;
      } else {
        const boldRegex = /\*\*(.*?)\*\*/g;
        let parts = line.split(boldRegex);
        let cursorX = marginLeft;
  
        parts.forEach((part, idx) => {
          const isBold = idx % 2 === 1;
          const words = part.split(" ");
  
          words.forEach((word) => {
            const testWord = word + " ";
            const wordWidth = doc.getTextWidth(testWord);
  
            if (cursorX + wordWidth > (210 - marginRight)) {
              // New line
              y += lineSpacing;
              if (y > 270) {
                doc.addPage();
                y = 20;
              }
              cursorX = marginLeft;
            }
  
            doc.setFont("helvetica", isBold ? "bold" : "normal");
            doc.text(word + " ", cursorX, y, { baseline: "top" });
            cursorX += wordWidth;
          });
        });
  
        y += lineSpacing;
      }
    });
  
    doc.save("VerifAI_Report.pdf");
  };
  

  const renderFormattedReport = (text) => {
    const safeText = typeof text === "string" ? text : String(text);
    const lines = safeText.split("\n");
  
    return lines.map((line, index) => {
      if (line.startsWith("##")) {
        // Heading
        return (
          <h2
            key={index}
            style={{
              fontSize: "1.5rem",
              color: "#1b3b6f",
              marginTop: "20px",
              textAlign: "left",
            }}
          >
            {line.replace(/^##\s*/, "")}
          </h2>
        );
      } else if (line.trim() === "") {
        // Blank line
        return <br key={index} />;
      } else {
        // Paragraph — handle bold
        const parts = line.split(/(\*\*.*?\*\*)/g); 
        return (
          <p
            key={index}
            style={{
              margin: "5px 0",
              lineHeight: "1.6",
              textAlign: "left",
            }}
          >
            {parts.map((part, idx) => {
              if (part.startsWith("**") && part.endsWith("**")) {
                return (
                  <strong key={idx}>
                    {part.slice(2, -2)}
                  </strong>
                );
              } else {
                return part;
              }
            })}
          </p>
        );
      }
    });
  };
  
  const cleanUpReportText = (rawText) => {
    let text = typeof rawText === "string" ? rawText : String(rawText);
  
    // 1. Remove "content,# " if it exists at the beginning
    if (text.startsWith("content,#")) {
      text = text.replace(/^content,#\s*/, "");
    }
  
    // 2. Remove anything after ",refusal" or similar artifacts
    const garbageIndex = text.indexOf(",refusal");
    if (garbageIndex !== -1) {
      text = text.substring(0, garbageIndex).trim();
    }
  
    return text;
  };  

  return (
    <div className="reports-page">
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

      <section className="reports-section">
        <h1 className="reports-title">Generate Report</h1>
        <p className="reports-description">
          Click the button below to generate a new report based on your model results.
        </p>

        <div className="reports-button-container">
          <button className="reports-generate-btn" onClick={handleGenerateReport} disabled={loading}>
            {loading ? "Generating..." : "Generate Report"}
          </button>
          <button className="reports-download-btn" onClick={handleDownloadReport}>
            <FaDownload /> Download PDF
          </button>
          <button className="reports-back-btn" onClick={() => navigate("/upload")}>
            <FaArrowLeft /> Back to Upload
          </button>
        </div>

        <div className="report-content">
          {reportText ? (
            renderFormattedReport(cleanUpReportText(reportText))
          ) : (
            <p className="report-placeholder">No report available. Generate a report to view it here.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default Reports;
