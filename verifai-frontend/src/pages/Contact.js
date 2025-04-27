import React, { useState } from "react";
import "../styles/pages/Contact.css";
import { Link } from "react-router-dom";

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
    <div className="contact-page">
      {/* Background Section (Same as Home Page) */}
      <section className="contact-header">
        <div className="container-contact">
          <h2>VERIFAI</h2>
          <div className="page-tab-contact">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>CONTACT</span>
          </div>
        </div>
      </section>

      {/* White Space & Contact Section */}
      <section className="contact-section">
        <div className="contact-form-container">
          <h1 className="contact-title">Contact Us</h1>
          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="contact-form-group">
              <label>Name <span className="contact-required">*</span></label>
              <input type="text" name="name" placeholder="Enter your name" required onChange={handleChange} />
            </div>
            <div className="contact-form-group">
              <label>Email <span className="contact-required">*</span></label>
              <input type="email" name="email" placeholder="Enter your email" required onChange={handleChange} />
            </div>
            <div className="contact-form-group">
              <label>Subject</label>
              <input type="text" name="subject" placeholder="Enter subject" onChange={handleChange} />
            </div>
            <div className="contact-form-group">
              <label>Message <span className="contact-required">*</span></label>
              <textarea name="message" placeholder="Write your message" required onChange={handleChange} />
            </div>
            <button type="submit" className="contact-button">Send Message</button>
          </form>
        </div>

        {/* Google Map Section */}
        <div className="contact-map">
          <iframe
            title="Google Map"
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3038.6432374842034!2d49.8468050762!3d40.3945989714432!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40307d6ee857fa47%3A0x67993e393222e8e2!2sADA%20University!5e0!3m2!1sen!2saz!4v1740091144163!5m2!1sen!2saz"
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>
      </section>

    </div>
  );
};

export default Contact;
