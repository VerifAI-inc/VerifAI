import React, { useState } from "react";
import "../styles/pages/Upload.css";

const Upload = () => {
  const [modelFile, setModelFile] = useState(null);
  const [datasetFile, setDatasetFile] = useState(null);
  const [labelName, setLabelName] = useState("");
  const [favorableLabel, setFavorableLabel] = useState("");
  const [protectedAttribute, setProtectedAttribute] = useState("");
  const [privilegedAttribute, setPrivilegedAttribute] = useState("");
  const [mitigators, setMitigators] = useState([]);
  const [dpModel, setDpModel] = useState("");
  const [uploadResult, setUploadResult] = useState(null);
  const [previewInfo, setPreviewInfo] = useState(null);

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  // New handler for model file preview
  const handleModelFileChange = async (e) => {
    const file = e.target.files[0];
    setModelFile(file);
    
    const formData = new FormData();
    formData.append("modelFile", file);
    formData.append("epsilon", "1.0");
    formData.append("num_features", "10");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/preview-model/", {
        method: "POST",
        headers: {
          "Authorization": "Token 89409bb7487029afdef8f93282c15a1d3b4aacdb",
        },
        body: formData,
      });
      const data = await response.json();
      console.log("Preview response:", data);
      setPreviewInfo(data);
    } catch (error) {
      console.error("Error during model preview:", error);
    }
  };

  const handleMitigatorChange = (e) => {
    const value = e.target.value;
    setMitigators((prev) =>
      prev.includes(value) ? prev.filter((m) => m !== value) : [...prev, value]
    );
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("modelFile", modelFile);
    formData.append("datasetFile", datasetFile);
    formData.append("labelName", labelName);
    formData.append("favorableLabel", favorableLabel);
    formData.append("protectedAttribute", protectedAttribute);
    formData.append("privilegedAttribute", privilegedAttribute);
    formData.append("dpModel", dpModel);
    formData.append("epsilon", "1.0");
    
    mitigators.forEach((mitigator) => formData.append("mitigators", mitigator));
    
    try {
      const response = await fetch("http://127.0.0.1:8000/api/upload/", {
        method: "POST",
        headers: {
          "Authorization": "Token 89409bb7487029afdef8f93282c15a1d3b4aacdb",
        },
        body: formData,
      });
      
      const data = await response.json();
      console.log("Response from server:", data);
      setUploadResult(data);
    } catch (error) {
      console.error("Error during file upload:", error);
    }
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
              <input type="file" accept=".pkl" onChange={handleModelFileChange} />
            </div>
            {/* Display preview information right after model upload */}
            {previewInfo && (
              <div className="model-preview">
                <h3>Uploaded Model</h3>
                {previewInfo.error ? (
                  <p>Error: {previewInfo.error}</p>
                ) : (
                  <>
                    <p>Model Name: {previewInfo.model_type}</p>
                    <p>DP Model Name: {previewInfo.dp_model_name}</p>
                  </>
                )}
              </div>
            )}
            <div className="form-group">
              <label>Label Name</label>
              <input type="text" placeholder="Enter label name" value={labelName} onChange={(e) => setLabelName(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Protected Attribute Name</label>
              <input type="text" placeholder="Enter protected attribute" value={protectedAttribute} onChange={(e) => setProtectedAttribute(e.target.value)} />
            </div>
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
        {uploadResult && (
          <div className="upload-result">
            <p>{uploadResult.message}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
