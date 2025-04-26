import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAllSprites, editSpriteImage, getSpriteHistory } from '../services/api';
import SpriteHistory, { SpriteVersion } from './SpriteHistory';

interface Sprite {
  id: string;
  url: string;
  description: string;
  parent_id?: string;
  edit_description?: string;
  created_at?: string;
}

interface SpriteHistoryData {
  current: Sprite;
  ancestors: Sprite[];
  children: Sprite[];
  timeline: Sprite[];
}

const SpriteDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [sprite, setSprite] = useState<Sprite | null>(null);
  const [displayedSprite, setDisplayedSprite] = useState<Sprite | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Edit state
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editPrompt, setEditPrompt] = useState<string>('');
  const [isEditLoading, setIsEditLoading] = useState<boolean>(false);
  
  // History state
  const [historyData, setHistoryData] = useState<SpriteHistoryData | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchSprite = async () => {
      if (!id) return;
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch sprite details
        const allSprites = await getAllSprites();
        const foundSprite = allSprites.find(s => s.id === id);
        
        if (foundSprite) {
          setSprite(foundSprite);
          setDisplayedSprite(foundSprite);
          
          // Fetch sprite history
          await fetchSpriteHistory(foundSprite.id);
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
  
  const fetchSpriteHistory = async (spriteId: string) => {
    try {
      setIsHistoryLoading(true);
      const history = await getSpriteHistory(spriteId);
      setHistoryData(history);
    } catch (err) {
      console.error('Error fetching sprite history:', err);
      // Don't set an error, just log it
    } finally {
      setIsHistoryLoading(false);
    }
  };

  const handleDownload = () => {
    if (!displayedSprite) return;
    
    const link = document.createElement('a');
    link.href = displayedSprite.url;
    link.download = `sprite-${displayedSprite.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCreateAnimation = () => {
    // Will implement animation creation later
    if (displayedSprite) {
      navigate(`/animation-generator?spriteId=${displayedSprite.id}`);
    }
  };
  
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sprite || !editPrompt.trim()) return;
    
    try {
      setIsEditLoading(true);
      setError(null);
      
      const updatedSprite = await editSpriteImage({
        spriteId: sprite.id,
        prompt: editPrompt
      });
      
      setSprite(updatedSprite);
      setDisplayedSprite(updatedSprite);
      setIsEditing(false);
      setEditPrompt('');
      
      // Refresh history to include the new edit
      await fetchSpriteHistory(updatedSprite.id);
    } catch (err) {
      setError('Failed to edit sprite. Please try again.');
      console.error(err);
    } finally {
      setIsEditLoading(false);
    }
  };
  
  // Convert Sprite to SpriteVersion
  const mapSpriteToVersion = (sprite: Sprite): SpriteVersion => {
    return {
      id: sprite.id,
      imageUrl: sprite.url,
      prompt: sprite.description,
      createdAt: sprite.created_at || new Date().toISOString()
    };
  };

  const handleSelectVersion = (version: SpriteVersion) => {
    // Find the corresponding sprite in the timeline
    const selectedSprite = historyData?.timeline.find(s => s.id === version.id);
    if (selectedSprite) {
      setDisplayedSprite(selectedSprite);
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

  if (error || !sprite || !displayedSprite) {
    return <div className="error-message">{error || 'Sprite not found'}</div>;
  }

  // Map the timeline sprites to SpriteVersion objects
  const spriteVersions = historyData?.timeline.map(mapSpriteToVersion) || [];

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
              <img src={displayedSprite.url} alt={displayedSprite.description} />
              {displayedSprite.id !== sprite.id && (
                <div className="viewing-version-notice">
                  Viewing previous version
                  <button 
                    className="btn-link"
                    onClick={() => setDisplayedSprite(sprite)}
                  >
                    Return to latest
                  </button>
                </div>
              )}
            </div>
            <div className="sprite-detail-info">
              <h3>Description</h3>
              <p>{displayedSprite.description}</p>
              
              {displayedSprite.edit_description && (
                <div className="edit-description">
                  <h4>Edit Description</h4>
                  <p>{displayedSprite.edit_description}</p>
                </div>
              )}
              
              <div className="sprite-detail-metadata">
                <p><strong>ID:</strong> {displayedSprite.id}</p>
                <p><strong>Format:</strong> PNG with transparency</p>
                {displayedSprite.created_at && (
                  <p><strong>Created:</strong> {new Date(displayedSprite.created_at).toLocaleString()}</p>
                )}
              </div>
              
              {isEditing ? (
                <div className="sprite-edit-form">
                  <h3>Edit Sprite</h3>
                  <form onSubmit={handleEditSubmit}>
                    <div className="form-group">
                      <label htmlFor="editPrompt" className="form-label">
                        Edit Instructions
                      </label>
                      <p className="form-description">
                        Describe the changes you want to make to this sprite.
                      </p>
                      <textarea
                        id="editPrompt"
                        className="form-input"
                        value={editPrompt}
                        onChange={(e) => setEditPrompt(e.target.value)}
                        placeholder="Example: Change the color to red, make it larger, add a hat, etc."
                        rows={4}
                        required
                      />
                    </div>
                    <div className="edit-form-actions">
                      <button
                        type="submit"
                        className="btn-primary"
                        disabled={isEditLoading || !editPrompt.trim()}
                      >
                        {isEditLoading ? 'Editing...' : 'Apply Changes'}
                      </button>
                      <button
                        type="button"
                        className="btn-secondary"
                        onClick={() => {
                          setIsEditing(false);
                          setEditPrompt('');
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                <div className="sprite-detail-actions">
                  <h3>Actions</h3>
                  <div className="action-buttons">
                    <button 
                      className="btn-primary"
                      onClick={handleCreateAnimation}
                    >
                      Create Animation
                    </button>
                    {displayedSprite.id === sprite.id && (
                      <button 
                        className="btn-secondary"
                        onClick={() => setIsEditing(true)}
                      >
                        Edit Sprite
                      </button>
                    )}
                    <button 
                      className="btn-secondary"
                      onClick={handleDownload}
                    >
                      Download Sprite
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {historyData && historyData.timeline.length > 1 && (
            <SpriteHistory 
              versions={spriteVersions}
              currentVersionId={displayedSprite.id}
              onSelectVersion={handleSelectVersion}
            />
          )}
        </div>
      </div>
      
      {isEditLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner" />
            <p>Editing sprite...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpriteDetail; 