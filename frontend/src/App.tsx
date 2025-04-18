import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import SpriteGenerator from './pages/SpriteGenerator';
import AnimationGenerator from './pages/AnimationGenerator';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/generate-sprite" element={<SpriteGenerator />} />
            <Route path="/generate-animation" element={<AnimationGenerator />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
