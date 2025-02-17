import React from "react";
import AppRoutes from "./routes/AppRoutes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

const App = () => {
  return (
    <>
      <Navbar />
      <div style={{ minHeight: "85vh" }}> {/* Ensures Footer stays at bottom */}
        <AppRoutes />
      </div>
      <Footer />
    </>
  );
};

export default App;