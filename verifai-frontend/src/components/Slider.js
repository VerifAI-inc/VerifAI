import React from "react";
import "../styles/components/Slider.css";

const Slider = ({ value, onChange, label = "Epsilon" }) => {
  // Define allowed epsilon values
  const epsilonValues = [0.1, 1, 5, 10];

  // Handle value change
  const handleChange = (event) => {
    const closest = epsilonValues.reduce((prev, curr) => 
      Math.abs(curr - event.target.value) < Math.abs(prev - event.target.value) ? curr : prev
    );
    onChange({ target: { value: closest } }); // Snap to closest allowed value
  };

  return (
    <div className="slider-wrapper">
      <label className="slider-label">{label}: {value}</label>
      <input
        type="range"
        min="0.1"
        max="10"
        step="any"
        value={value}
        onChange={handleChange}
        className="slider-input"
      />
    </div>
  );
};

export default Slider;