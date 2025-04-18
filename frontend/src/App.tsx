import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/sprite-generator" element={<div>Sprite Generator</div>} />
            <Route path="/animation-generator" element={<div>Animation Generator</div>} />
            <Route path="/library" element={<div>Library</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
