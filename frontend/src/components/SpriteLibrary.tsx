import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllSprites } from '../services/api';

interface Sprite {
  id: string;
  url: string;
  description: string;
}

const SpriteLibrary: React.FC = () => {
  const navigate = useNavigate();
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

  const handleSpriteClick = (spriteId: string) => {
    navigate(`/sprites/${spriteId}`);
  };

  const handleDownload = (e: React.MouseEvent, sprite: Sprite) => {
    e.stopPropagation(); // Prevent navigation to detail page
    
    const link = document.createElement('a');
    link.href = sprite.url;
    link.download = `sprite-${sprite.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleAnimateClick = (e: React.MouseEvent, spriteId: string) => {
    e.stopPropagation(); // Prevent navigation to detail page
    navigate(`/animation-generator?spriteId=${spriteId}`);
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
                <div 
                  key={sprite.id} 
                  className="sprite-card"
                  onClick={() => handleSpriteClick(sprite.id)}
                >
                  <div className="sprite-image-wrapper">
                    <img src={sprite.url} alt={sprite.description} className="sprite-image" />
                  </div>
                  <div className="sprite-details">
                    <p className="sprite-description">{sprite.description}</p>
                    <div className="sprite-actions">
                      <button
                        className="btn-secondary"
                        onClick={(e) => handleDownload(e, sprite)}
                      >
                        Download
                      </button>
                      <button 
                        className="btn-secondary"
                        onClick={(e) => handleAnimateClick(e, sprite.id)}
                      >
                        Animate
                      </button>
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