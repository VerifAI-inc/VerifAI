import React from "react";
import "../styles/pages/Home.css"; 
import { Link } from "react-router-dom";
import Slider from "react-slick";

// Import images
import privacyImage from "../assets/images/privacy-image.webp";
import fairnessImage from "../assets/images/fairness-image.webp";
import member1 from "../assets/images/member1.jpeg";
import member2 from "../assets/images/member2.jpg";
import member3 from "../assets/images/member3.jpg";
import member4 from "../assets/images/member4.jpg";

// Custom arrow components
const CustomPrevArrow = (props) => {
  const { onClick } = props;
  return <div className="home-slick-prev-custom" onClick={onClick}>&#10094;</div>;
};

const CustomNextArrow = (props) => {
  const { onClick } = props;
  return <div className="home-slick-next-custom" onClick={onClick}>&#10095;</div>; 
};

const Home = () => {
  const feedbacks = [
    {
      id: 1,
      name: "John Doe",
      role: "Business Owner",
      feedback: "VerifAI helped us identify biases in our AI model and improved our decision-making process significantly.",
    },
    {
      id: 2,
      name: "Jane Smith",
      role: "AI Researcher",
      feedback: "A fantastic tool that ensures fairness in machine learning models. Highly recommended!",
    },
    {
      id: 3,
      name: "David Wilson",
      role: "Software Engineer",
      feedback: "With VerifAI, we improved the accuracy of our predictions while maintaining ethical AI standards.",
    },
    {
      id: 4,
      name: "Sophia Martinez",
      role: "Data Scientist",
      feedback: "An essential tool for anyone working with AI fairness and privacy. Easy to use and insightful!",
    },
  ];

  // Slider settings
  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 4000,
    prevArrow: <CustomPrevArrow />,
    nextArrow: <CustomNextArrow />,
  };

  return (
    <div className="home-container">
      {/* Page Title Before About  Section */}
      <section className="page-title-home">
        <div className="container-home">
          {/* <h2>VerifAI</h2> */}
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>ABOUT US</span>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about-main-home">
        <div className="container-home">
          <div className="row-home">
            <div className="col-6-home">
              <div className="about-main-left-home">
                <h2>About VerifAI</h2>
                <p>
                  At VerifAI, privacy is a core concern. Our AI ensures that data remains secure and
                  anonymized while evaluating fairness and bias in models.
                </p>
              </div>
            </div>
            <div className="col-6-home">
              <div className="about-main-right-home">
                <img src={privacyImage} alt="Privacy" className="about-image-home" />
              </div>
            </div>
          </div>
        </div>

        <div className="container-home">
          <div className="row-home">
            <div className="col-6-home">
              <div className="about-main-left2-home">
                <img src={fairnessImage} alt="Fairness" className="about-image-home" />
              </div>
            </div>
            <div className="col-6-home">
              <div className="about-main-right2-home">
                <h2>Why VerifAI?</h2>
                <p>
                    <strong>Automated ML Fairness & Privacy Evaluation:</strong> Enables businesses, researchers, and developers to analyze how fair and privacy-safe their ML models are.  
                </p>
                <p>
                    <strong>Trade-off Analysis:</strong> Helps users adjust epsilon values interactively to find the right balance between privacy, fairness, and accuracy.  
                </p>
                <p>
                    <strong>Real-World Compliance:</strong> Supports fairness & privacy regulations (GDPR, AI Ethics Guidelines).  
                </p>
                <p>
                    <strong>Visualization & Reporting:</strong> Generates detailed interactive graphs, tables, and reports for stakeholders.  
                </p>
                <p>
                    <strong>No Deep ML Knowledge Required:</strong> Makes privacy & fairness evaluation accessible to non-experts.  
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Investment Section Title */}
      <section className="page-title-investment">
        <div className="container-home">
          <h2>Investment</h2>
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>INVESTMENT</span>
          </div>
        </div>
      </section>

      {/* Investment Invitation Text & Video */}
      <section className="investment-invite">
        <div className="container-home">
          <h2>Interested in Investing?</h2>
          <p>
            If you want to invest in VerifAI and be part of our exciting journey
            towards building fair and privacy-preserving AI solutions, please contact us.
          </p>
        </div>
      </section>

      <section className="investment-video-section">
        <div className="container-home">
          <div className="video-frame">
            <video 
              controls 
              autoPlay 
              muted 
              loop 
              preload="metadata"
              className="investment-video"
              >
              <source src="/videos/investment-promo.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      </section>

      {/* Page Title Before Client Feedback Section */}
      <section className="page-title-team">
        <div className="container-home">
          <h2>Client Feedback</h2>
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>CLIENT FEEDBACK</span>
          </div>
        </div>
      </section>

      {/* Client Feedback Section */}
      <section className="client-feedback-home">
        <div className="container-home">
          <h2>WHAT OUR CLIENTS SAY</h2>
          <Slider {...settings}>
            {feedbacks.map((feedback) => (
              <div className="feedback-box-home" key={feedback.id}>
                <p className="feedback-text-home">"{feedback.feedback}"</p>
                <h3 className="feedback-name-home">{feedback.name}</h3>
                <span className="feedback-role-home">{feedback.role}</span>
              </div>
            ))}
          </Slider>
        </div>
      </section>

      {/* Page Title Before Team Section */}
      <section className="page-title-team">
        <div className="container-home">
          <h2>Meet Our Team</h2>
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>OUR TEAM</span>
          </div>
        </div>
      </section>

      {/* Meet Our Team Section */}
      <section className="our-team-home">
        <div className="container-home">
          <h2>MEET OUR TEAM</h2>
          <div className="row-home">
            {[
              {
                name: "ILHAMA NOVRUZOVA",
                image: member1,
                role: "CO-Founder"
              },
              {
                name: "NATAVAN HASANOVA",
                image: member2,
                role: "CO-Founder"
              },
              {
                name: "KHALID MAMMADOV",
                image: member3,
                role: "CO-Founder"
              },
              {
                name: "BAHRUZ GURBANLI",
                image: member4,
                role: "CO-Founder"
              }
            ].map((member, index) => (
              <div className="team-box-home" key={index}>
                <div className="team-img-home">
                  <img src={member.image} alt={`Team Member ${index + 1}`} />
                </div>
                <div className="team-person-home">
                  <p>{member.name}</p>
                  <span>{member.role}</span>
                </div>
                <div className="team-person-social-home">
                  <a href="https://instagram.com/verifai.tech"><i className="fa-brands fa-instagram"></i></a>
                  <a href="https://instagram.com/verifai.tech"><i className="fa-brands fa-facebook-f"></i></a>
                  <a href="https://instagram.com/verifai.tech"><i className="fa-brands fa-linkedin-in"></i></a>
                  <a href="https://instagram.com/verifai.tech"><i className="fa-brands fa-github"></i></a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;