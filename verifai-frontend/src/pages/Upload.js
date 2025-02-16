import React from "react";
import { useNavigate } from "react-router-dom";

const Upload = () => {
  const navigate = useNavigate();

  const handleResults = () => {
    navigate("/results");
  };

  return (
    <div>
      <h1>Upload Your Dataset & Model</h1>

      <button onClick={handleResults}>See Results</button>
    </div>
  );
};

export default Upload;