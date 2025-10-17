// components/Navbar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <div className="brand-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="currentColor" />
              <path
                d="M3 17L12 22L21 17"
                stroke="currentColor"
                strokeWidth="2"
              />
              <path
                d="M3 12L12 17L21 12"
                stroke="currentColor"
                strokeWidth="2"
              />
            </svg>
          </div>
          <span className="brand-text">SupplyAI</span>
        </div>

        <div className="navbar-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
          >
            Home
          </Link>
          <Link
            to="/chat"
            className={`nav-link ${
              location.pathname === "/chat" ? "active" : ""
            }`}
          >
            Chat
          </Link>
          <Link
            to="/admin"
            className={`nav-link ${
              location.pathname === "/admin" ? "active" : ""
            }`}
          >
            Admin
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
