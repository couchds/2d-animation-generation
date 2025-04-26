import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAllSprites } from '../services/api';

interface Sprite {
  id: string;
  url: string;
  description: string;
}

const SpriteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [sprite, setSprite] = useState<Sprite | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSprite = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // For now, we'll fetch all sprites and find the one with matching ID
        // Later, we can create a dedicated API endpoint for this
        const allSprites = await getAllSprites();
        const foundSprite = allSprites.find(s => s.id === id);
        
        if (foundSprite) {
          setSprite(foundSprite);
        } else {
          setError('Sprite not found');
        }
      } catch (err) {
        setError('Failed to load sprite details');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSprite();
  }, [id]);

  const handleDownload = () => {
    if (!sprite) return;
    
    const link = document.createElement('a');
    link.href = sprite.url;
    link.download = `sprite-${sprite.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCreateAnimation = () => {
    // Will implement animation creation later
    if (sprite) {
      navigate(`/animation-generator?spriteId=${sprite.id}`);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
        <p>Loading sprite details...</p>
      </div>
    );
  }

  if (error || !sprite) {
    return <div className="error-message">{error || 'Sprite not found'}</div>;
  }

  return (
    <div className="container mt-8">
      <div className="card">
        <div className="card-header">
          <h2>Sprite Details</h2>
          <button 
            className="btn-secondary"
            onClick={() => navigate(-1)}
          >
            Back to Library
          </button>
        </div>
        <div className="card-body">
          <div className="sprite-detail-layout">
            <div className="sprite-detail-image">
              <img src={sprite.url} alt={sprite.description} />
            </div>
            <div className="sprite-detail-info">
              <h3>Description</h3>
              <p>{sprite.description}</p>
              
              <div className="sprite-detail-metadata">
                <p><strong>ID:</strong> {sprite.id}</p>
                <p><strong>Format:</strong> PNG with transparency</p>
              </div>
              
              <div className="sprite-detail-actions">
                <h3>Actions</h3>
                <div className="action-buttons">
                  <button 
                    className="btn-primary"
                    onClick={handleCreateAnimation}
                  >
                    Create Animation
                  </button>
                  <button 
                    className="btn-secondary"
                    onClick={handleDownload}
                  >
                    Download Sprite
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpriteDetail; 