import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/pages/Upload.css";

const Upload = () => {
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

  const getAuthToken = () => localStorage.getItem('token');

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const handleModelFileChange = async (e) => {
    const file = e.target.files[0];
    setUploadModelFile(file);

    const formData = new FormData();
    formData.append("modelFile", file);
    formData.append("epsilon", "1.0");
    formData.append("num_features", "10");

    try {
      const token = getAuthToken();
      const response = await fetch("http://127.0.0.1:8000/api/preview-model/", {
        method: "POST",
        headers: {
          "Authorization": `Token ${token}`,
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
    setUploadDpModel("");formData.append("dpModel", uploadDpModel);
    formData.append("epsilon", "1.0");

    uploadMitigators.forEach((mitigator) => formData.append("mitigators", mitigator));

    try {
      const token = getAuthToken();
      const response = await fetch("http://127.0.0.1:8000/api/upload/", {
        method: "POST",
        headers: {
          "Authorization": `Token ${token}`,
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
      <section className="page-title-home">
        <div className="container-home">
          <h2>VerifAI</h2>
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>UPLOAD</span>
          </div>
        </div>
      </section>

      <div className="upload-main">
        <h1 className="upload-title">Upload Data</h1>
        <div className="upload-card-wrapper">
          <div className="upload-card">
            <div className="upload-form-section">
              <div className="upload-form-column">
                <div className="upload-form-group">
                  <label>Upload Model (.pkl file)</label>
                  <input
                    type="file"
                    accept=".pkl"
                    onChange={handleModelFileChange}
                  />
                </div>

                {/* Model Preview */}
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

                <div className="upload-form-group">
                  <label>Label Name</label>
                  <input
                    type="text"
                    placeholder="Enter label name"
                    value={uploadLabelName}
                    onChange={(e) => setUploadLabelName(e.target.value)}
                  />
                </div>

                <div className="upload-form-group">
                  <label>Protected Attribute Name</label>
                  <input
                    type="text"
                    placeholder="Enter protected attribute"
                    value={uploadProtectedAttribute}
                    onChange={(e) => setUploadProtectedAttribute(e.target.value)}
                  />
                </div>

                <div className="upload-form-group upload-mitigators-group">
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
              </div>

              <div className="upload-form-column">
                <div className="upload-form-group">
                  <label>Upload Clean Dataset (.csv file)</label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileChange(e, setUploadDatasetFile)}
                  />
                </div>

                <div className="upload-form-group">
                  <label>Privileged Attribute</label>
                  <input
                    type="text"
                    placeholder="Enter privileged attribute"
                    value={uploadPrivilegedAttribute}
                    onChange={(e) => setUploadPrivilegedAttribute(e.target.value)}
                  />
                </div>

                <div className="upload-form-group">
                  <label>Favorable Label Name</label>
                  <input
                    type="text"
                    placeholder="Enter favorable label name"
                    value={uploadFavorableLabel}
                    onChange={(e) => setUploadFavorableLabel(e.target.value)}
                  />
                </div>
              </div>
            </div>

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
      </div>
    </div>
  );
};

export default Upload;
