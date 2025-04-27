import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="text-center max-w-3xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Create Stunning 2D Animations
        </h1>
        <p className="text-lg text-gray-600 mb-12">
          Generate beautiful sprites and animations with our easy-to-use tools.
          Perfect for game development, web design, and creative projects.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link 
            to="/sprite-generator" 
            className="card p-8 text-center group"
          >
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-indigo-600 group-hover:text-indigo-700 transition-colors duration-200" 
                   fill="none" 
                   stroke="currentColor" 
                   viewBox="0 0 24 24" 
                   xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Sprite Generator</h2>
            <p className="text-gray-600">Create custom sprites with our intuitive generator</p>
          </Link>

          <Link 
            to="/animation-generator" 
            className="card p-8 text-center group"
          >
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-indigo-600 group-hover:text-indigo-700 transition-colors duration-200" 
                   fill="none" 
                   stroke="currentColor" 
                   viewBox="0 0 24 24" 
                   xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Animation Generator</h2>
            <p className="text-gray-600">Bring your sprites to life with smooth animations</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home; 