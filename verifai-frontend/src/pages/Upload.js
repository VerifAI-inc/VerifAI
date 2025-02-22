import React, { useState } from "react";
import "../styles/Upload.css";

const Upload = () => {
  const [modelFile, setModelFile] = useState(null);
  const [datasetFile, setDatasetFile] = useState(null);
  const [labelName, setLabelName] = useState("");
  const [favorableLabel, setFavorableLabel] = useState("");
  const [protectedAttribute, setProtectedAttribute] = useState("");
  const [privilegedAttribute, setPrivilegedAttribute] = useState("");
  const [mitigators, setMitigators] = useState([]);
  const [dpModel, setDpModel] = useState("");

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const handleMitigatorChange = (e) => {
    const value = e.target.value;
    setMitigators((prev) =>
      prev.includes(value) ? prev.filter((m) => m !== value) : [...prev, value]
    );
  };

  const handleSubmit = () => {
    console.log("Model File:", modelFile?.name);
    console.log("Dataset File:", datasetFile?.name);
    console.log("Label Name:", labelName);
    console.log("Favorable Label:", favorableLabel);
    console.log("Protected Attribute:", protectedAttribute);
    console.log("Privileged Attribute:", privilegedAttribute);
    console.log("Selected Mitigators:", mitigators);
    console.log("DP Model:", dpModel);
  };

  return (
    <div className="upload-container">
      <h1 className="upload-title">Upload Data</h1>
      <div className="upload-card">
        <div className="form-section">
          {/* Left Column */}
          <div className="form-column">
            <div className="form-group">
              <label>Upload Model (.pkl file)</label>
              <input type="file" accept=".pkl" onChange={(e) => handleFileChange(e, setModelFile)} />
            </div>

            <div className="form-group">
              <label>Label Name</label>
              <input type="text" placeholder="Enter label name" value={labelName} onChange={(e) => setLabelName(e.target.value)} />
            </div>

            <div className="form-group">
              <label>Protected Attribute Name</label>
              <input type="text" placeholder="Enter protected attribute" value={protectedAttribute} onChange={(e) => setProtectedAttribute(e.target.value)} />
            </div>

            {/* Mitigators Section Moved to Right */}
            <div className="form-group mitigators-group">
              <label>Choose Mitigators (Multiple Select)</label>
              <div className="mitigators-container">
                {["Synthetic Oversampling", "Rew", "Dir", "Eg"].map((mitigator) => (
                  <label key={mitigator} className="mitigator-option">
                    <input
                      type="checkbox"
                      value={mitigator}
                      checked={mitigators.includes(mitigator)}
                      onChange={handleMitigatorChange}
                    />
                    {mitigator}
                  </label>
                ))}
            </div>
          </div>
        </div>

          {/* Right Column */}
          <div className="form-column">
            <div className="form-group">
              <label>Upload Clean Dataset (.csv file)</label>
              <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, setDatasetFile)} />
            </div>

            <div className="form-group">
              <label>Privileged Attribute</label>
              <input type="text" placeholder="Enter privileged attribute" value={privilegedAttribute} onChange={(e) => setPrivilegedAttribute(e.target.value)} />
            </div>

            <div className="form-group">
              <label>Favorable Label Name</label>
              <input type="text" placeholder="Enter favorable label name" value={favorableLabel} onChange={(e) => setFavorableLabel(e.target.value)} />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button className="upload-button" onClick={handleSubmit}>
          GET RESULTS
        </button>
      </div>
    </div>
  );
};

export default Upload;
