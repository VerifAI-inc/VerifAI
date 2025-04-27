import React, { useState } from "react";
import "../styles/components/Slider.css";

const Slider = ({ value, onChange, label = "Epsilon" }) => {
  const epsilonValues = [0.1, 1, 5, 10]; // Allowed epsilon values
  const [tempValue, setTempValue] = useState(value); // Temporary value for smooth dragging

  // When dragging, update tempValue without snapping
  const handleDrag = (event) => {
    setTempValue(event.target.value); // Move freely
  };

  // When releasing, snap to the closest valid epsilon
  const handleRelease = () => {
    const closest = epsilonValues.reduce((prev, curr) =>
      Math.abs(curr - tempValue) < Math.abs(prev - tempValue) ? curr : prev
    );
    setTempValue(closest); // Ensure slider shows the snapped value
    onChange({ target: { value: closest } }); // Notify parent component
  };

  // When clicking on a legend, move the slider smoothly to that value
  const handleLegendClick = (selectedValue) => {
    setTempValue(selectedValue); // Show smooth movement
    setTimeout(() => onChange({ target: { value: selectedValue } }), 200); // Delay snap effect
  };

  return (
    <div className="slider-wrapper">
      <label className="slider-label">{label}: {tempValue}</label>

      {/* Slider Container */}
      <div className="slider-container">

        {/* The Actual Slider */}
        <input
          type="range"
          min="0.1"
          max="10"
          step="any"
          value={tempValue}
          onChange={handleDrag} // Allows free movement
          onMouseUp={handleRelease} // Snaps after release
          onTouchEnd={handleRelease} // For mobile support
          className="slider-input"
        />

        {/* Legend Markers Below the Slider */}
        <div className="slider-legends">
          {epsilonValues.map((val) => (
            <div
              key={val}
              className="slider-legend"
              style={{ left: `${((val - 0.1) / (10 - 0.1)) * 100}%` }} // Dynamically place marker
              onClick={() => handleLegendClick(val)} // Move to clicked value
            >
              {val}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Slider;