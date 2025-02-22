import React, { useEffect } from "react";
import "../styles/Home.css";

const Home = () => {
  useEffect(() => {
    const handleMouseMove = (e) => {
      const { clientX: x, clientY: y } = e;
      document.documentElement.style.setProperty("--mouseX", `${x}px`);
      document.documentElement.style.setProperty("--mouseY", `${y}px`);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>VerifAI</h1>
        <p>Empowering AI Solutions</p>
        <button className="cta-button">Get Started</button>
      </div>
    </div>
  );
};

export default Home;