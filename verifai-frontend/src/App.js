import React from "react";
import { useLocation } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

const App = () => {
  const location = useLocation(); 

  return (
    <>
      <Navbar />
      <div style={{ minHeight: "85vh" }}> {/* Ensures Footer stays at bottom */}
        <AppRoutes />
      </div>
      {/* Hide Footer only on the Signup Page */}
      {location.pathname !== "/signup" && <Footer />}
    </>
  );
};

export default App;
