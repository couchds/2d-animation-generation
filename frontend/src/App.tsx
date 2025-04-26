import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import SpriteGenerator from './components/SpriteGenerator';
import SpriteLibrary from './components/SpriteLibrary';
import SpriteDetail from './components/SpriteDetail';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/sprite-generator" element={<SpriteGenerator />} />
            <Route path="/animation-generator" element={<div>Animation Generator</div>} />
            <Route path="/library" element={<SpriteLibrary />} />
            <Route path="/sprites/:id" element={<SpriteDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
