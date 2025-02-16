import React from "react";

const Footer = () => {
  return (
    <footer style={{ textAlign: "center", padding: "10px", borderTop: "1px solid #ccc", marginTop: "20px" }}>
      <p>© {new Date().getFullYear()} VerifAI. All rights reserved.</p>
      <p>Contact us at <a href="mailto:support@verifai.com">support@verifai.com</a></p>
    </footer>
  );
};

export default Footer;