import React, { useState } from "react";
import "../styles/Upload.css";

const Upload = () => {
  const [dpModel, setDpModel] = useState("");
  const [modelParam, setModelParam] = useState("");
  const [mitigator, setMitigator] = useState("");

  const handleSubmit = () => {
    console.log("DP Model:", dpModel);
    console.log("Model Parameter:", modelParam);
    console.log("Mitigator:", mitigator);
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h1 className="upload-title">Upload</h1>

        <div className="form-group">
          <label>Choose DP Model Type</label>
          <select
            value={dpModel}
            onChange={(e) => setDpModel(e.target.value)}
          >
            <option value="">Select DP Model</option>
            <option value="dp1">DP Model 1</option>
            <option value="dp2">DP Model 2</option>
            <option value="dp3">DP Model 3</option>
          </select>
        </div>

        <div className="form-group">
          <label>Choose Model Parameters</label>
          <select
            value={modelParam}
            onChange={(e) => setModelParam(e.target.value)}
          >
            <option value="">Select Model Parameter</option>
            <option value="param1">Parameter 1</option>
            <option value="param2">Parameter 2</option>
            <option value="param3">Parameter 3</option>
          </select>
        </div>

        <div className="form-group">
          <label>Choose Mitigator</label>
          <select
            value={mitigator}
            onChange={(e) => setMitigator(e.target.value)}
          >
            <option value="">Select Mitigator</option>
            <option value="mitigator1">Mitigator 1</option>
            <option value="mitigator2">Mitigator 2</option>
            <option value="mitigator3">Mitigator 3</option>
          </select>
        </div>

        <button className="upload-button" onClick={handleSubmit}>
          GET RESULTS
        </button>
      </div>
    </div>
  );
};

export default Upload;