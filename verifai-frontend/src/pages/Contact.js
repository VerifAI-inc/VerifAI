import React, { useState } from "react";
import "../styles/Contact.css";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Contact Form Data:", formData);
    alert("Message sent successfully!");
  };

  return (
    <div className="contact-container">
      {/* Left Section - Contact Info */}
      <div className="contact-left">
        <h2>Get in Touch</h2>
        <p>Have a question? Feel free to reach out, and we’ll get back to you as soon as possible.</p>
        <div className="contact-info">
          <p>📍 Ahmadbey Aghaoglu str. 61 Baku, 1008</p>
          <p>📧 support@verifai.com</p>
          <p>📞 +1 (123) 456-7890</p>
        </div>
      </div>

      {/* Right Section - Contact Form */}
      <div className="contact-right">
        <h1 className="contact-title">Contact Us</h1>
        <form className="contact-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name <span className="required">*</span></label>
            <input type="text" name="name" placeholder="Enter your name" required onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Email <span className="required">*</span></label>
            <input type="email" name="email" placeholder="Enter your email" required onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Subject</label>
            <input type="text" name="subject" placeholder="Enter subject" onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Message <span className="required">*</span></label>
            <textarea name="message" placeholder="Write your message" required onChange={handleChange} />
          </div>
          <button type="submit" className="contact-button">Send Message</button>
        </form>
        
        
        {/* Small Google Map Below the Form */}
        <div className="contact-map">
        <iframe
          title="Google Map"
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3038.6432374842034!2d49.8468050762!3d40.3945989714432!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40307d6ee857fa47%3A0x67993e393222e8e2!2sADA%20University!5e0!3m2!1sen!2saz!4v1740091144163!5m2!1sen!2saz"
          style={{ border: "none", borderRadius: "10px", marginTop: "15px", width: "110%", maxWidth: "600px", height: "250px" }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        ></iframe>
        </div>
      </div>
    </div>
  );
};

export default Contact;
