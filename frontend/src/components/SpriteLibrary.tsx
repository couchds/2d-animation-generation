import React, { useState, useEffect } from 'react';
import { getAllSprites } from '../services/api';

interface Sprite {
  id: string;
  url: string;
  description: string;
}

const SpriteLibrary: React.FC = () => {
  const [sprites, setSprites] = useState<Sprite[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSprites = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getAllSprites();
        setSprites(data);
      } catch (err) {
        setError('Failed to load sprites. Please try again later.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSprites();
  }, []);

  const handleDownload = (sprite: Sprite) => {
    const link = document.createElement('a');
    link.href = sprite.url;
    link.download = `sprite-${sprite.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
        <p>Loading sprites...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="container mt-8">
      <div className="card">
        <div className="card-header">
          <h2>Sprite Library</h2>
          <p>Browse all generated sprites</p>
        </div>
        <div className="card-body">
          {sprites.length === 0 ? (
            <p>No sprites have been generated yet. Go to the Sprite Generator to create some!</p>
          ) : (
            <div className="sprite-grid">
              {sprites.map((sprite) => (
                <div key={sprite.id} className="sprite-card">
                  <div className="sprite-image-wrapper">
                    <img src={sprite.url} alt={sprite.description} className="sprite-image" />
                  </div>
                  <div className="sprite-details">
                    <p className="sprite-description">{sprite.description}</p>
                    <div className="sprite-actions">
                      <button
                        className="btn-secondary"
                        onClick={() => handleDownload(sprite)}
                      >
                        Download
                      </button>
                      <button className="btn-secondary">Animate</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpriteLibrary; 