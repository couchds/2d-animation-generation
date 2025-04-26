import React, { useState } from 'react';
import { generateSprite } from '../services/api';
import { SpriteVersion } from './SpriteHistory';
import SpriteHistory from './SpriteHistory';

const examplePrompts = [
  {
    title: "Cute Slime",
    prompt: "A cute slime character with big eyes, light blue color, smiling face, bouncy body, pixel art style."
  },
  {
    title: "Pixel Knight",
    prompt: "A pixel art knight character with silver armor, blue cape, holding a sword and shield, heroic stance."
  },
  {
    title: "Magical Cat",
    prompt: "A magical cat with purple fur, glowing yellow eyes, stars floating around, wearing a wizard hat, cute pixel art style."
  }
];

const SpriteGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [spriteHistory, setSpriteHistory] = useState<SpriteVersion[]>([]);
  const [currentVersionId, setCurrentVersionId] = useState<string>('');

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a description for your sprite.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await generateSprite(prompt);
      setGeneratedImage(response.url);

      // Create a new sprite version
      const newVersion: SpriteVersion = {
        id: Date.now().toString(), // Generate a unique ID
        imageUrl: response.url,
        prompt: prompt,
        createdAt: new Date().toISOString()
      };

      // Update history with the new version
      setSpriteHistory(prev => [newVersion, ...prev]);
      setCurrentVersionId(newVersion.id);
    } catch (err) {
      console.error('Error generating sprite:', err);
      setError('Failed to generate sprite. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectVersion = (version: SpriteVersion) => {
    if (version) {
      setGeneratedImage(version.imageUrl);
      setCurrentVersionId(version.id);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Sprite Generator</h2>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="prompt" className="form-label">Describe your character or sprite</label>
            <p className="form-description">Be specific about colors, style, features, and mood for best results.</p>
            
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
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="form-input"
              placeholder="Example: A cute blue dragon with big eyes, small wings, and a friendly smile in pixel art style."
              rows={4}
            />
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Sprite'}
          </button>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Creating your sprite... This may take a moment.</p>
          </div>
        )}
        
        {generatedImage && !loading && (
          <div className="generated-content">
            <div className="generated-image-container">
              <div className="image-wrapper">
                <img src={generatedImage} alt="Generated sprite" className="generated-image" />
              </div>
              <div className="image-actions">
                <button className="btn-secondary">Download</button>
                <button className="btn-secondary">Edit</button>
              </div>
            </div>
            
            {spriteHistory.length > 0 && (
              <SpriteHistory 
                versions={spriteHistory} 
                currentVersionId={currentVersionId}
                onSelectVersion={handleSelectVersion} 
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SpriteGenerator; 