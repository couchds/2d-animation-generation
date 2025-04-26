import React, { useState } from 'react';
import { generateSprite } from '../services/api';

const examplePrompts = [
  {
    title: "Cute Slime",
    prompt: "A cute blue slime with big round eyes and a happy expression. The slime should be semi-transparent and have a slight glow effect."
  },
  {
    title: "Pixel Knight",
    prompt: "A pixel art style knight in shining armor. The character has a silver helmet with a red plume, a blue cape, and a golden sword. The armor has intricate engravings and the character is in a battle-ready stance."
  },
  {
    title: "Magical Cat",
    prompt: "A mystical cat with purple fur and glowing green eyes. It has a star-shaped marking on its forehead and is surrounded by floating magical orbs. The cat is sitting elegantly with its tail wrapped around its paws."
  }
];

const SpriteGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const response = await generateSprite(prompt);
      setGeneratedImage(response.url);
    } catch (err) {
      setError('Failed to generate sprite. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;
    const link = document.createElement('a');
    link.href = generatedImage;
    link.download = 'generated-sprite.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Generate Base Sprite</h2>
        <p>Create a base sprite with a transparent background for your character</p>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="prompt" className="form-label">
              Describe your character
            </label>
            <p className="form-description">
              Be specific about the character's appearance, including colors, style, and any unique features.
            </p>
            <div className="example-prompts">
              {examplePrompts.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-prompt-btn"
                  onClick={() => handleExampleClick(example.prompt)}
                >
                  {example.title}
                </button>
              ))}
            </div>
            <textarea
              id="prompt"
              className="form-input"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Example: A cute blue slime with big round eyes and a happy expression. The slime should be semi-transparent and have a slight glow effect."
              rows={4}
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !prompt.trim()}
          >
            {isLoading ? 'Generating...' : 'Generate Base Sprite'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}

        {isLoading && (
          <div className="loading-spinner">
            <div className="spinner" />
            <p>Generating your sprite...</p>
          </div>
        )}

        {generatedImage && (
          <div className="generated-image-container">
            <h3>Generated Sprite</h3>
            <div className="image-wrapper">
              <img
                src={generatedImage}
                alt="Generated sprite"
                className="generated-image"
              />
            </div>
            <div className="image-actions">
              <button className="btn-secondary" onClick={handleDownload}>
                Download Image
              </button>
              <button className="btn-secondary">Create Animation</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpriteGenerator; 