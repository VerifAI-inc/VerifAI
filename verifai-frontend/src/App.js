import React from "react";
import { useLocation } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

const App = () => {
  const location = useLocation(); 

  const pageClass = location.pathname === "/" ? "home" : "other-pages";

  return (
    <div className={pageClass}>
      <Navbar />
      <div className="main-content">
        <AppRoutes />
      </div>
      <Footer />
    </div>
  );
};

export default App;
