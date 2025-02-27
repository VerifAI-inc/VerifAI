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
    <div>
    <div className="home-container">
      <div className="hero-section">
        <h1>VerifAI</h1>
        <p>Empowering AI Solutions</p>
        <button className="cta-button">Get Started</button>
      </div>
    </div>
    <div className="about-container">
      <h2>About</h2>
      <p>
        VerifAI is a platform that empowers AI solutions by providing a
        comprehensive suite of tools for data labeling, model training, and
        model evaluation. Our platform is designed to be user-friendly and
        accessible to users with varying levels of technical expertise. Whether
        you are a seasoned data scientist or a beginner in the field of AI, you
        can leverage VerifAI to build and deploy AI solutions that meet your
        needs.
      </p>
    </div>
    </div>
  );
};

export default Home;