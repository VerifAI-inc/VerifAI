import React from "react";
import { useLocation } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

const App = () => {
  const location = useLocation(); 

  // Apply different backgrounds based on the route
  const pageClass = location.pathname === "/" ? "home" : "other-pages";

  return (
    <div className={pageClass}>
      <Navbar />
      <div style={{ minHeight: "85vh" }}> {/* Ensures Footer stays at bottom */}
        <AppRoutes />
      </div>
      {/* Hide Footer only on the Signup Page */}
      {location.pathname !== "/signup" && <Footer />}
    </div>
  );
};

export default App;
