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
      <div className={`page-container ${location.pathname.substring(1)}-page`}>
        <AppRoutes />
      </div>
      <Footer />
    </>
  );
};

export default App;
