import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/pages/Upload.css";
import API_BASE_URL from "../config";

const Upload = () => {
  const navigate = useNavigate();

  const [uploadModelFile, setUploadModelFile] = useState(null);
  const [uploadDatasetFile, setUploadDatasetFile] = useState(null);
  const [uploadLabelName, setUploadLabelName] = useState("");
  const [uploadFavorableLabel, setUploadFavorableLabel] = useState("");
  const [uploadProtectedAttribute, setUploadProtectedAttribute] = useState("");
  const [uploadPrivilegedAttribute, setUploadPrivilegedAttribute] = useState("");
  const [uploadMitigators, setUploadMitigators] = useState([]);
  const [uploadDpModel, setUploadDpModel] = useState("");
  const [uploadResult, setUploadResult] = useState(null);
  const [previewInfo, setPreviewInfo] = useState(null);

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const getAuthHeader = () => ({
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  });

  const handleModelFileChange = async (e) => {
    const file = e.target.files[0];
    setUploadModelFile(file);

    const formData = new FormData();
    formData.append("modelFile", file);
    formData.append("epsilon", "1.0");
    formData.append("num_features", "10");

    try {
      const response = await fetch(`${API_BASE_URL}/api/preview-model/`, {
        method: "POST",
        headers: getAuthHeader(),
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
    setUploadMitigators((prev) =>
      prev.includes(value) ? prev.filter((m) => m !== value) : [...prev, value]
    );
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("modelFile", uploadModelFile);
    formData.append("datasetFile", uploadDatasetFile);
    formData.append("labelName", uploadLabelName);
    formData.append("favorableLabel", uploadFavorableLabel);
    formData.append("protectedAttribute", uploadProtectedAttribute);
    formData.append("privilegedAttribute", uploadPrivilegedAttribute);
    setUploadDpModel("");
    formData.append("dpModel", uploadDpModel);
    formData.append("epsilon", "1.0");

    uploadMitigators.forEach((mitigator) => formData.append("mitigators", mitigator));

    try {
      const response = await fetch(`${API_BASE_URL}/api/upload/`, {
        method: "POST",
        headers: getAuthHeader(),
        body: formData,
      });
      const data = await response.json();
      console.log("Upload response:", data);
      setUploadResult(data);
    } catch (error) {
      console.error("Error during file upload:", error);
    }
  };

  return (
    <div className="upload-page">
      <section className="upload-header">
        <div className="upload-container">
          <div className="upload-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>Upload</span>
          </div>
        </div>
      </section>

      <section className="upload-form">
        <div className="upload-card">
          <h2>Upload Model & Dataset</h2>
          <div className="card-description">
            <p>Use this form to upload your model and clean dataset for analysis.</p>
            <p>Provide labels and attributes below, and select any fairness mitigators to apply.</p>
          </div>

          <div className="form-row">
            <div className="form-group half-width">
              <label>Upload Model <span className="file-type">(.pkl file)</span></label>
              <input type="file" accept=".pkl" onChange={handleModelFileChange} />
              {uploadModelFile && <span className="filename">{uploadModelFile.name}</span>}
            </div>

            <div className="form-group half-width">
              <label>Upload Clean Dataset <span className="file-type">(.csv file)</span></label>
              <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, setUploadDatasetFile)} />
              {uploadDatasetFile && <span className="filename">{uploadDatasetFile.name}</span>}
            </div>
          </div>

          {previewInfo && (
            <div className="form-group">
              <h3>Model Preview</h3>
              {previewInfo.error ? (
                <p className="error-message">Error: {previewInfo.error}</p>
              ) : (
                <>
                  <p>Model Type: {previewInfo.model_type}</p>
                  <p>DP Model: {previewInfo.dp_model_name}</p>
                </>
              )}
            </div>
          )}

          <div className="form-row">
            <div className="form-group half-width">
              <label>Label Name</label>
              <input
                type="text"
                placeholder="Enter label name"
                value={uploadLabelName}
                onChange={(e) => setUploadLabelName(e.target.value)}
              />
            </div>
            <div className="form-group half-width">
              <label>Favorable Label Name</label>
              <input
                type="text"
                placeholder="e.g., 1"
                value={uploadFavorableLabel}
                onChange={(e) => setUploadFavorableLabel(e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group half-width">
              <label>Protected Attribute Name</label>
              <input
                type="text"
                placeholder="e.g., gender"
                value={uploadProtectedAttribute}
                onChange={(e) => setUploadProtectedAttribute(e.target.value)}
              />
            </div>
            <div className="form-group half-width">
              <label>Privileged Attribute Name</label>
              <input
                type="text"
                placeholder="e.g., male"
                value={uploadPrivilegedAttribute}
                onChange={(e) => setUploadPrivilegedAttribute(e.target.value)}
              />
            </div>
          </div>

          <div className="upload-mitigators-group">
            <label>Choose Mitigators (Multiple Select)</label>
            <div className="upload-mitigators-container">
              {["Synthetic Oversampling", "Rew", "Dir", "Eg"].map((mitigator) => (
                <label key={mitigator} className="upload-mitigator-option">
                  <input
                    type="checkbox"
                    value={mitigator}
                    checked={uploadMitigators.includes(mitigator)}
                    onChange={handleMitigatorChange}
                  />
                  {mitigator}
                </label>
              ))}
            </div>
          </div>

          <div className="form-row" style={{ justifyContent: "center", gap: "20px" }}>
            <button className="submit-btn" style={{ maxWidth: "260px" }} onClick={handleSubmit}>Start Training</button>
            <button className="submit-btn" style={{ maxWidth: "260px" }} onClick={() => navigate("/results")}>See Results</button>
          </div>

          {uploadResult && (
            <div className="form-group">
              <p>{uploadResult.message}</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Upload;