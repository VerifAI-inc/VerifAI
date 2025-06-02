import React, { useState } from 'react';
import { Link, useNavigate } from "react-router-dom";
import "../styles/pages/Services.css";

export default function Services() {
  const navigate = useNavigate();
  const [modelFile, setModelFile] = useState(null);
  const [datasetFile, setDatasetFile] = useState(null);
  const [goal, setGoal] = useState('');
  const [weights, setWeights] = useState({ fairness: 33, privacy: 33, accuracy: 34 });
  const [errors, setErrors] = useState({ model: '', dataset: '' });

  const handleWeightChange = (key, value) => {
    value = parseInt(value);
    const otherKeys = Object.keys(weights).filter(k => k !== key);
    const remaining = 100 - value;

    const sumOthers = weights[otherKeys[0]] + weights[otherKeys[1]];
    let updated = { ...weights, [key]: value };

    if (sumOthers === 0) {
      updated[otherKeys[0]] = Math.floor(remaining / 2);
      updated[otherKeys[1]] = remaining - updated[otherKeys[0]];
    } else {
      updated[otherKeys[0]] = Math.round((weights[otherKeys[0]] / sumOthers) * remaining);
      updated[otherKeys[1]] = remaining - updated[otherKeys[0]];
    }

    setWeights(updated);
  };

  const handleModelUpload = (e) => {
    const file = e.target.files[0];
    if (file && !file.name.endsWith('.pkl')) {
      setErrors(prev => ({ ...prev, model: 'Only .pkl files are accepted for model upload.' }));
      setModelFile(null);
    } else {
      setErrors(prev => ({ ...prev, model: '' }));
      setModelFile(file);
    }
  };

  const handleDatasetUpload = (e) => {
    const file = e.target.files[0];
    if (file && !file.name.endsWith('.csv')) {
      setErrors(prev => ({ ...prev, dataset: 'Only .csv files are accepted for dataset upload.' }));
      setDatasetFile(null);
    } else {
      setErrors(prev => ({ ...prev, dataset: '' }));
      setDatasetFile(file);
    }
  };

  return (
    <div className="services-page">
      <section className="services-header">
        <div className="services-container">
          <div className="services-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>Services</span>
          </div>
        </div>
      </section>

      <section className="services-form">
        <div className="services-card">
          <h2>Submit Model & Dataset for Evaluation</h2>
          <div className="card-description">
            <p>
              This form allows you to submit your model and  dataset
              for evaluation. You will describe your intended use case and distribute
              importance weights across fairness, privacy, and accuracy.
            </p>
            <p>
              Our system will assess your model based on the uploaded files and
              configuration, and generate tailored insights.
            </p>
          </div>

          <div className="form-row">
            <div className="form-group half-width">
              <label htmlFor="model-upload">1. Upload Your Model <span className="file-type">(.pkl file)</span></label>
              <input id="model-upload" type="file" accept=".pkl" onChange={handleModelUpload} />
              {modelFile && <span className="filename">{modelFile.name}</span>}
              {errors.model && <span className="error-message">{errors.model}</span>}
            </div>

            <div className="form-group half-width">
              <label htmlFor="dataset-upload">2. Upload Your Dataset <span className="file-type">(.csv file)</span></label>
              <input id="dataset-upload" type="file" accept=".csv" onChange={handleDatasetUpload} />
              {datasetFile && <span className="filename">{datasetFile.name}</span>}
              {errors.dataset && <span className="error-message">{errors.dataset}</span>}
            </div>
          </div>

          <div className="form-group goal-box">
            <label htmlFor="goal-input">3. Describe Your Intended Goal</label>
            <textarea
              id="goal-input"
              rows="4"
              placeholder="What do you want to achieve?"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
            ></textarea>
          </div>

          <div className="form-group">
            <label className="slider-group-label">4. Allocate Importance Weights (Total = 100%)</label>
            <div className="sliders-horizontal">
              <div className="slider-box">
                <label>Fairness: {weights.fairness}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.fairness}
                  onChange={(e) => handleWeightChange('fairness', e.target.value)}
                />
              </div>
              <div className="slider-box">
                <label>Privacy: {weights.privacy}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.privacy}
                  onChange={(e) => handleWeightChange('privacy', e.target.value)}
                />
              </div>
              <div className="slider-box">
                <label>Accuracy: {weights.accuracy}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={weights.accuracy}
                  onChange={(e) => handleWeightChange('accuracy', e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="form-group">
            <button className="submit-btn">Submit</button>
          </div>
        </div>
      </section>
    </div>
  );
}
