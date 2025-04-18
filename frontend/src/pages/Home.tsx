import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">
        Welcome to 2D Animation Generator
      </h1>
      <p className="text-xl text-gray-600 mb-12">
        Create beautiful 2D sprites and animations using AI
      </p>
      <div className="flex justify-center space-x-8">
        <Link
          to="/generate-sprite"
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg"
        >
          Generate Sprite
        </Link>
        <Link
          to="/generate-animation"
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg"
        >
          Generate Animation
        </Link>
      </div>
    </div>
  );
};

export default Home; 