import React, { useState } from "react";
import Slider from "../components/Slider";
import "../styles/Global.css";

const Results = () => {
  const [epsilon, setEpsilon] = useState(1.0); // Default ε value

  const handleSliderChange = (event) => {
    setEpsilon(event.target.value);
  };

  return (
    <div>
      <h1>Results Page</h1>

      {/* Epsilon Slider */}
      <Slider value={epsilon} onChange={handleSliderChange} label="Epsilon (ε)" />

      {/* Graph Sections */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
        <div style={{ width: "48%", border: "1px solid black", padding: "10px" }}>
          <h2>Without DP</h2>
          {/* Graphs will be placed here */}
        </div>

        <div style={{ width: "48%", border: "1px solid black", padding: "10px" }}>
          <h2>With DP</h2>
          {/* Graphs will be placed here */}
        </div>
      </div>

      {/* Buttons Section */}
      <div style={{ marginTop: "20px" }}>
        <button>Download Graphs</button>
        <button>See Tables</button>
        <button>See Report</button>
      </div>
    </div>
  );
};

export default Results;