import { useState } from 'react';
import { spriteService } from '../services/spriteService';

export const SpriteGenerator = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [sprite, setSprite] = useState<{ url: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!description) {
      setError('Please enter a description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await spriteService.generateSprite(description);
      setSprite(response);
    } catch (err) {
      setError('Failed to generate sprite. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Generate Base Sprite</h1>
      
      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Character Description
        </label>
        <textarea
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your character..."
        />
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <button
        className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate Sprite'}
      </button>

      {sprite && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Generated Sprite</h2>
          <img
            src={sprite.url}
            alt="Generated sprite"
            className="max-w-full rounded-lg shadow-lg"
          />
        </div>
      )}
    </div>
  );
}; 