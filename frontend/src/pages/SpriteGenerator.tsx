import React, { useState } from 'react';
import axios from 'axios';

const SpriteGenerator: React.FC = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [spriteUrl, setSpriteUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/sprites/generate', {
        description
      });
      setSpriteUrl(response.data.url);
    } catch (err) {
      setError('Failed to generate sprite. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Generate Sprite</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Sprite Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            rows={4}
            placeholder="Describe the sprite you want to generate..."
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Sprite'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {spriteUrl && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Generated Sprite</h2>
          <img
            src={spriteUrl}
            alt="Generated sprite"
            className="max-w-full h-auto rounded-lg shadow-lg"
          />
        </div>
      )}
    </div>
  );
};

export default SpriteGenerator; 