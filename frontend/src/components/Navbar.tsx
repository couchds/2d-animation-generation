import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800">
              2D Animation Generator
            </Link>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/generate-sprite"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Generate Sprite
            </Link>
            <Link
              to="/generate-animation"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Generate Animation
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 