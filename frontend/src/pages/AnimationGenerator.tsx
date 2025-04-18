import { useState } from 'react';
import { animationService } from '../services/animationService';

const ANIMATION_TYPES = [
  'idle',
  'walk',
  'run',
  'jump',
  'attack',
  'defend',
  'cast',
  'death'
];

export const AnimationGenerator = () => {
  const [baseSpriteId, setBaseSpriteId] = useState('');
  const [animationType, setAnimationType] = useState('');
  const [loading, setLoading] = useState(false);
  const [animation, setAnimation] = useState<{ url: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!baseSpriteId || !animationType) {
      setError('Please select a base sprite and animation type');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await animationService.generateAnimation(
        baseSpriteId,
        animationType
      );
      setAnimation(response);
    } catch (err) {
      setError('Failed to generate animation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Generate Animation</h1>
      
      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Base Sprite ID
        </label>
        <input
          type="text"
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={baseSpriteId}
          onChange={(e) => setBaseSpriteId(e.target.value)}
          placeholder="Enter base sprite ID"
        />
      </div>

      <div className="mb-6">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Animation Type
        </label>
        <select
          className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={animationType}
          onChange={(e) => setAnimationType(e.target.value)}
        >
          <option value="">Select animation type</option>
          {ANIMATION_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <button
        className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50"
        onClick={handleGenerate}
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate Animation'}
      </button>

      {animation && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Generated Animation</h2>
          <img
            src={animation.url}
            alt="Generated animation"
            className="max-w-full rounded-lg shadow-lg"
          />
        </div>
      )}
    </div>
  );
}; 