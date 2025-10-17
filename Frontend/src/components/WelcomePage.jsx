// components/WelcomePage.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./WelcomePage.css";

const WelcomePage = () => {
  const features = [
    {
      icon: "💬",
      title: "AI-Powered Chat",
      description:
        "Get intelligent supplier recommendations with detailed reasoning",
    },
    {
      icon: "📊",
      title: "Data Analysis",
      description: "Analyze supplier data and performance metrics",
    },
    {
      icon: "🔍",
      title: "Smart Search",
      description: "Find the best suppliers based on your specific criteria",
    },
    {
      icon: "⚡",
      title: "Fast Responses",
      description: "Get instant answers powered by advanced AI",
    },
  ];

  return (
    <div className="welcome-container">
      <div className="welcome-hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Intelligent Supplier
            <span className="gradient-text"> Recommendations</span>
          </h1>
          <p className="hero-description">
            Leverage AI to find the perfect suppliers for your business needs.
            Get data-driven insights and comprehensive analysis in seconds.
          </p>
          <div className="hero-actions">
            <Link to="/chat" className="btn btn-primary">
              Start Chatting
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 12H19M19 12L12 5M19 12L12 19"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </Link>
            <Link to="/admin" className="btn btn-secondary">
              Manage Files
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="chat-preview">
            <div className="message-preview user">
              Find suppliers for electronics
            </div>
            <div className="message-preview bot">
              Based on your requirements, I recommend...
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2 className="features-title">Why Choose SupplyAI?</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
