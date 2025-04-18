import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          2D Animation Generator
        </Link>
        <div className="navbar-links">
          <Link to="/sprite-generator" className="navbar-link">
            Sprite Generator
          </Link>
          <Link to="/animation-generator" className="navbar-link">
            Animation Generator
          </Link>
          <Link to="/library" className="navbar-link">
            Library
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 