import React from "react";
import "../styles/pages/Home.css"; 
import { Link } from "react-router-dom";
import Slider from "react-slick";

// Import images
import privacyImage from "../assets/images/privacy-image.webp";
import fairnessImage from "../assets/images/fairness-image.webp";
import member1 from "../assets/images/member1.jpg";
import member2 from "../assets/images/member2.jpg";
import member3 from "../assets/images/member3.jpg";
import member4 from "../assets/images/member4.jpg";

<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
/>

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
  const quotes = [
    {
      id: 1,
      name: "Max Tegmark",
      role: "Physicist and AI Researcher",
      // feedback: "The only industry that is completely unregulated right now, which has no safety standards, is AI.",
      feedback: (
        <>
          The only industry that is completely unregulated right now,<br />
          which has no safety standards, is AI.
        </>
      ),
    },
    {
      id: 2,
      name: "Amazon",
      role: "E-commerce company",
      feedback: (
        <>
          From the outset, we have prioritized responsible AI innovation<br />
          by embedding safety, fairness, robustness, security, and privacy<br />
          into our development processes.
        </>
      ),
    },
    {
      id: 3,
      name: "Timnit Gebru",
      role: "AI Ethics Researcher",
      // feedback: "Fairness is not just a feature—it must be a foundation of every AI system we build.",
      feedback: (
        <>
          Fairness is not just a feature—<br />
          it must be a foundation of every AI system we build.
        </>
      ),
    },
    {
      id: 4,
      name: "Bruce Schneier",
      role: "Security Technologist",
      feedback: (
        <>
          As we automate and analyze more, we must secure more.<br />
          An AI system without security is a risk multiplier.
        </>
      ),
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
      <section className="home-header">
        <div className="home-second-container">
          <div className="home-breadcrumb">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>About Us</span>
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
                <p className="feature-point">
                  <i className="fas fa-check-circle"></i> No-Code Platform
                </p>
                <p className="feature-point">
                  <i className="fas fa-users"></i> Suitable for Researchers & Enterprises
                </p>
                <p className="feature-point">
                  <i className="fas fa-shield-alt"></i> Fairness, Privacy & Security Focused
                </p>
                <p className="feature-point">
                  <i className="fas fa-brain"></i> No Technical Expertise Needed
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
                <p className="feature-point">
                  <i className="fas fa-robot"></i> Automated ML Fairness, Privacy & Security
                </p>
                <p className="feature-point">
                  <i className="fas fa-balance-scale"></i> Trade-off Analysis
                </p>
                <p className="feature-point">
                  <i className="fas fa-gavel"></i> Real-World Compliances
                </p>
                <p className="feature-point">
                  <i className="fas fa-chart-line"></i> Visualization & Reports
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
            <iframe
              className="investment-video"
              src="https://www.youtube.com/embed/yTtGi3oBoWo"
              title="VerifAI Investment Video"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      </section>

      {/* Page Title Before Client Feedback Section */}
      <section className="page-title-team">
        <div className="container-home">
          <h2>Why Now?</h2>
          <div className="page-tab-home">
            <Link to="/">HOME</Link>
            <i className="fas fa-angle-right"></i>
            <span>WHY NOW</span>
          </div>
        </div>
      </section>

      {/* Why Now Quote Section */}
      <section className="why-now-home">
        <div className="container-home">
          <h2>WHY NOW?</h2>
          <Slider {...settings}>
            {quotes.map((item) => (
              <div className="why-now-box-home" key={item.id}>
                <p className="why-now-text-home">"{item.feedback}"</p>
                <h3 className="why-now-name-home">{item.name}</h3>
                <span className="why-now-role-home">{item.role}</span>
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
                role: (
                  <>
                    CO-Founder<br />Chief Executive Officer
                  </>
                ),
                socials: {
                  linkedin: "https://www.linkedin.com/in/ilhamanovruzova/",
                  github: "https://github.com/inovruzova"
                }
              },
              {
                name: "NATAVAN HASANOVA",
                image: member2,
                role: (
                  <>
                    CO-Founder<br />Software Engineer
                  </>
                ), 
                socials: {
                  linkedin: "https://www.linkedin.com/in/hasanovanatavan/",
                  github: "https://github.com/nqasanova"
                }
              },
              {
                name: "KHALID MAMMADOV",
                image: member3,
                role: (
                  <>
                    CO-Founder<br />Product Manager
                  </>
                ),                 
                socials: {
                  linkedin: "https://www.linkedin.com/in/khalid-mammad/",
                  github: "https://github.com/khaleed-mammad"
                }
              },
              {
                name: "BAHRUZ GURBANLI",
                image: member4,
                role: (
                  <>
                    CO-Founder<br />Software Engineer
                  </>
                ),                 
                socials: {
                  linkedin: "https://www.linkedin.com/in/behruzgurbanli/",
                  github: "https://github.com/behruzgurbanli"
                }
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
                  <a href={member.socials.linkedin} target="_blank" rel="noopener noreferrer">
                    <i className="fa-brands fa-linkedin-in"></i>
                  </a>
                  <a href={member.socials.github} target="_blank" rel="noopener noreferrer">
                    <i className="fa-brands fa-github"></i>
                  </a>
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