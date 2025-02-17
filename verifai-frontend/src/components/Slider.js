import React from "react";

const Slider = ({ value, onChange, min = 0.1, max = 10.0, step = 0.1, label = "Epsilon" }) => {
  return (
    <div style={{ margin: "10px 0" }}>
      <label>{label}: {value}</label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        style={{ width: "100%" }}
      />
    </div>
  );
};

export default Slider;