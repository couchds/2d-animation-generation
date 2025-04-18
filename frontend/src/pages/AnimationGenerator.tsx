import React, { useState } from 'react';
import axios from 'axios';

const AnimationGenerator: React.FC = () => {
  const [spriteId, setSpriteId] = useState('');
  const [animationType, setAnimationType] = useState('idle');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [animationUrl, setAnimationUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/animations/generate', {
        sprite_id: spriteId,
        animation_type: animationType
      });
      setAnimationUrl(response.data.url);
    } catch (err) {
      setError('Failed to generate animation. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Generate Animation</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="spriteId" className="block text-sm font-medium text-gray-700">
            Sprite ID
          </label>
          <input
            type="text"
            id="spriteId"
            value={spriteId}
            onChange={(e) => setSpriteId(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Enter the sprite ID to animate"
            required
          />
        </div>

        <div>
          <label htmlFor="animationType" className="block text-sm font-medium text-gray-700">
            Animation Type
          </label>
          <select
            id="animationType"
            value={animationType}
            onChange={(e) => setAnimationType(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="idle">Idle</option>
            <option value="walk">Walk</option>
            <option value="run">Run</option>
            <option value="jump">Jump</option>
            <option value="attack">Attack</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Animation'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {animationUrl && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Generated Animation</h2>
          <img
            src={animationUrl}
            alt="Generated animation"
            className="max-w-full h-auto rounded-lg shadow-lg"
          />
        </div>
      )}
    </div>
  );
};

export default AnimationGenerator; 