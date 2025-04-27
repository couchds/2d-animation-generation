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
  const [editVariations, setEditVariations] = useState<Sprite[]>([]);
  const [isSelectingVariation, setIsSelectingVariation] = useState<boolean>(false);
  const [numVariations, setNumVariations] = useState<number>(3);
  
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
      console.log(`Fetching history for sprite ID: ${spriteId}`);
      
      const response = await fetch(`http://localhost:8000/api/sprites/history/${spriteId}`);
      
      if (!response.ok) {
        throw new Error(`API returned status: ${response.status} ${response.statusText}`);
      }
      
      const history = await response.json();
      console.log("Sprite history data (raw):", history);
      
      // Validate the response structure
      if (!history || typeof history !== 'object' || !history.timeline) {
        console.error("Invalid history data format:", history);
        throw new Error("Invalid history data format returned from API");
      }
      
      // Check if the arrays are present
      if (!Array.isArray(history.timeline) || !Array.isArray(history.ancestors) || !Array.isArray(history.children)) {
        console.error("Missing required arrays in history data:", history);
        throw new Error("Missing required arrays in history data");
      }
      
      // Debug the history data 
      console.log("Timeline items:", history.timeline.length);
      console.log("Ancestors:", history.ancestors.length);
      console.log("Children:", history.children.length);
      console.log("Current sprite:", history.current?.id);
      
      setHistoryData(history);
    } catch (err) {
      console.error('Error fetching sprite history:', err);
      // Show an error message but don't fail completely
      setError(prev => prev || 'Failed to load sprite history. Some functionality may be limited.');
    } finally {
      setIsHistoryLoading(false);
    }
  };
  
  // Add a debug function to manually fetch history
  const debugRefetchHistory = async () => {
    if (displayedSprite) {
      console.log("Manually refetching history...");
      await fetchSpriteHistory(displayedSprite.id);
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
      
      const variations = await editSpriteImage({
        spriteId: sprite.id,
        prompt: editPrompt,
        num_variations: numVariations
      });
      
      if (variations && variations.length > 0) {
        // Store the variations for selection
        setEditVariations(variations);
        setIsSelectingVariation(true);
        setIsEditing(false);
      } else {
        throw new Error("No variations were returned");
      }
    } catch (err) {
      setError('Failed to edit sprite. Please try again.');
      console.error(err);
    } finally {
      setIsEditLoading(false);
    }
  };
  
  const handleSelectVariation = async (selectedSprite: Sprite) => {
    // Make this sprite the selected "base" image
    try {
      setIsEditLoading(true);
      
      // Set the selected variation as the new sprite
      setSprite(selectedSprite);
      setDisplayedSprite(selectedSprite);
      
      // Mark this sprite as a base image
      // TODO: If needed, add a backend endpoint to mark a sprite as the base image
      
      // Reset state
      setIsSelectingVariation(false);
      setEditVariations([]);
      setEditPrompt('');
      
      // Refresh history to include the new edit
      await fetchSpriteHistory(selectedSprite.id);
    } catch (err) {
      setError('Failed to select variation. Please try again.');
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
      createdAt: sprite.created_at || new Date().toISOString(),
      editDescription: sprite.edit_description,
      isRoot: sprite.parent_id === null || sprite.parent_id === undefined
    };
  };

  const handleSelectVersion = (version: SpriteVersion) => {
    // Find the corresponding sprite in the timeline
    const selectedSprite = historyData?.timeline.find(s => s.id === version.id);
    if (selectedSprite) {
      setDisplayedSprite(selectedSprite);
    }
  };

  // Find the index of the currently displayed sprite in the timeline
  const currentIndex = historyData?.timeline.findIndex(s => s.id === displayedSprite?.id) ?? -1;
  const hasPrevious = currentIndex > 0;
  const hasNext = historyData && currentIndex < historyData.timeline.length - 1;

  // Debug logging
  console.log("Current displayedSprite:", displayedSprite);
  console.log("historyData:", historyData);
  console.log("Current index:", currentIndex);
  console.log("Has previous:", hasPrevious);
  console.log("Has next:", hasNext);

  // Handler for navigation buttons
  const handleNavigation = (direction: 'prev' | 'next') => {
    if (!historyData) return;
    
    const newIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex >= 0 && newIndex < historyData.timeline.length) {
      setDisplayedSprite(historyData.timeline[newIndex]);
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
              
              {/* Version navigation controls */}
              {historyData && historyData.timeline.length > 1 && (
                <div className="version-navigation-controls">
                  <button 
                    className="btn-primary btn-nav"
                    disabled={!hasPrevious}
                    onClick={() => handleNavigation('prev')}
                  >
                    ← Previous Version
                  </button>
                  <span className="version-indicator">
                    Version {currentIndex + 1} of {historyData.timeline.length}
                  </span>
                  <button 
                    className="btn-primary btn-nav"
                    disabled={!hasNext}
                    onClick={() => handleNavigation('next')}
                  >
                    Next Version →
                  </button>
                </div>
              )}
              
              {/* Direct parent/child navigation */}
              {historyData ? (
                <div className="parent-child-navigation">
                  <div style={{ marginBottom: '10px', padding: '5px', backgroundColor: '#f0f0f0', color: 'black' }}>
                    Debug Info:
                    <ul>
                      <li>History Loaded: {historyData ? "Yes" : "No"}</li>
                      <li>Timeline Length: {historyData?.timeline.length || 0}</li>
                      <li>Ancestors: {historyData?.ancestors.length || 0}</li>
                      <li>Children: {historyData?.children.length || 0}</li> 
                      <li>Current Index: {currentIndex}</li>
                      <li>Has Parent: {displayedSprite?.parent_id ? "Yes" : "No"}</li>
                      <li>Parent ID: {displayedSprite?.parent_id || "None"}</li>
                    </ul>
                  </div>
                  
                  {displayedSprite.parent_id && (
                    <button 
                      className="btn-secondary btn-parent"
                      onClick={() => {
                        const parentSprite = historyData.ancestors.find(s => s.id === displayedSprite.parent_id);
                        if (parentSprite) {
                          setDisplayedSprite(parentSprite);
                        }
                      }}
                    >
                      View Parent Sprite
                    </button>
                  )}
                  
                  {historyData.children.length > 0 && historyData.children.some(child => child.id !== sprite.id) && (
                    <div className="children-selector">
                      <span>Child Sprites: </span>
                      {historyData.children.map(child => (
                        <button 
                          key={child.id}
                          className={`btn-secondary btn-child ${displayedSprite.id === child.id ? 'active' : ''}`}
                          onClick={() => setDisplayedSprite(child)}
                        >
                          {child.edit_description ? child.edit_description.substring(0, 20) + '...' : 'Version ' + (historyData.timeline.findIndex(s => s.id === child.id) + 1)}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="debug-panel" style={{ margin: '1.5rem 0', padding: '1rem', backgroundColor: '#fff0f0', borderRadius: '0.5rem', border: '1px solid #ffcccb' }}>
                  <h4>History Data Not Available</h4>
                  <p>The sprite history data is not loaded even though this sprite has a parent ID: {displayedSprite?.parent_id}</p>
                  <button 
                    className="btn-secondary"
                    onClick={debugRefetchHistory}
                    style={{ marginTop: '10px' }}
                  >
                    Manually Fetch History
                  </button>
                </div>
              )}
              
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
                {displayedSprite.parent_id && (
                  <p><strong>Parent Sprite:</strong> {displayedSprite.parent_id}</p>
                )}
                {historyData && (
                  <p><strong>Version:</strong> {historyData.timeline.findIndex(s => s.id === displayedSprite.id) + 1} of {historyData.timeline.length}</p>
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
                    
                    <div className="form-group">
                      <label htmlFor="numVariations" className="form-label">
                        Number of Variations
                      </label>
                      <p className="form-description">
                        Choose how many variations to generate (1-5). More variations give you more options but take longer to generate.
                      </p>
                      <div className="variations-selector">
                        <input 
                          type="range" 
                          id="numVariations" 
                          min="1" 
                          max="5" 
                          value={numVariations} 
                          onChange={(e) => setNumVariations(parseInt(e.target.value))}
                          className="variations-slider"
                        />
                        <div className="variations-value">{numVariations}</div>
                      </div>
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
          
          {historyData && historyData.timeline.length > 0 && (
            <div className="sprite-timeline-section">
              <div className="sprite-timeline-header">
                <h3>Sprite Evolution</h3>
                <p>This sprite has {historyData.timeline.length} version{historyData.timeline.length !== 1 ? 's' : ''} in its history.</p>
              </div>
              <SpriteHistory 
                versions={spriteVersions}
                currentVersionId={displayedSprite.id}
                onSelectVersion={handleSelectVersion}
              />
            </div>
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
      
      {isSelectingVariation && (
        <div className="variation-selection-overlay">
          <div className="variation-selection-container">
            <h2>Choose a Variation</h2>
            <p>Select one of the {editVariations.length} variations below to apply your edit: <strong>{editPrompt}</strong></p>
            
            <div className="variation-grid">
              {editVariations.map((variation, index) => (
                <div key={variation.id} className="variation-item">
                  <div className="variation-image-container">
                    <img 
                      src={variation.url} 
                      alt={`Variation ${index + 1}`} 
                      className="variation-image"
                    />
                  </div>
                  <button
                    className="btn-primary"
                    onClick={() => handleSelectVariation(variation)}
                  >
                    Select Variation {index + 1}
                  </button>
                </div>
              ))}
            </div>
            
            <button
              className="btn-secondary variation-cancel-btn"
              onClick={() => {
                setIsSelectingVariation(false);
                setEditVariations([]);
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpriteDetail; 