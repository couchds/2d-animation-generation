import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useLocation, useNavigate } from 'react-router-dom';

// Add this CSS to your index.css file if it doesn't exist already
// If you prefer, you can keep it inline as className props
/*
.animation-frames-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.frame-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  cursor: pointer;
}

.frame-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: #d1d5db;
}

.frame-card.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.frame-image-wrapper {
  padding: 1rem;
  background-color: #f9fafb;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  position: relative;
}

.frame-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.frame-details {
  padding: 1rem;
}

.frame-actions {
  display: flex;
  gap: 0.5rem;
}

.frame-number {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #3b82f6;
  color: white;
  border-radius: 9999px;
  font-weight: 600;
}
*/

const AnimationGenerator: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [spriteId, setSpriteId] = useState('');
  const [spriteName, setSpriteName] = useState('');
  const [spriteImage, setSpriteImage] = useState('');
  const [animationType, setAnimationType] = useState('idle');
  const [numFrames, setNumFrames] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [animationUrl, setAnimationUrl] = useState('');
  const [animationId, setAnimationId] = useState('');
  const [allAnimations, setAllAnimations] = useState<any[]>([]);
  const [allFrames, setAllFrames] = useState<any[]>([]);
  const [selectedFrames, setSelectedFrames] = useState<string[]>([]);
  const [spritesheetGenerating, setSpritesheetGenerating] = useState(false);
  const [spritesheetUrl, setSpritesheetUrl] = useState('');
  const [activeAnimationType, setActiveAnimationType] = useState('idle');
  const [fetchingFrames, setFetchingFrames] = useState(false);
  
  // Animation preview state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [animationFps, setAnimationFps] = useState(12);
  const animationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Parse the sprite ID from the URL query parameters
    const queryParams = new URLSearchParams(location.search);
    const id = queryParams.get('spriteId');
    
    if (id) {
      setSpriteId(id);
      // Fetch sprite details to show the name and image
      fetchSpriteDetails(id);
      // Fetch existing animations for this sprite
      fetchSpriteAnimations(id);
    }
  }, [location]);

  // When animation type changes, filter and fetch frames
  useEffect(() => {
    if (spriteId && activeAnimationType && allAnimations.length > 0) {
      fetchFramesForAnimationType(activeAnimationType);
    }
  }, [activeAnimationType, allAnimations, spriteId]);
  
  // Animation playback effect
  useEffect(() => {
    if (isPlaying && selectedFrames.length > 0) {
      // Clear any existing interval
      if (animationIntervalRef.current) {
        clearInterval(animationIntervalRef.current);
      }
      
      // Start a new interval
      animationIntervalRef.current = setInterval(() => {
        setCurrentFrameIndex(prevIndex => {
          // Loop back to the first frame when we reach the end
          return (prevIndex + 1) % selectedFrames.length;
        });
      }, 1000 / animationFps); // Convert fps to milliseconds
    } else {
      // Stop the animation
      if (animationIntervalRef.current) {
        clearInterval(animationIntervalRef.current);
        animationIntervalRef.current = null;
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (animationIntervalRef.current) {
        clearInterval(animationIntervalRef.current);
      }
    };
  }, [isPlaying, selectedFrames, animationFps]);
  
  // Reset current frame index when selected frames change
  useEffect(() => {
    setCurrentFrameIndex(0);
  }, [selectedFrames]);

  const fetchSpriteDetails = async (id: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/sprites/${id}`);
      setSpriteName(response.data.description || 'Unnamed Sprite');
      setSpriteImage(response.data.url);
    } catch (err) {
      console.error('Failed to fetch sprite details:', err);
      setError('Failed to fetch sprite details.');
    }
  };

  const fetchSpriteAnimations = async (id: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/animations/sprite/${id}`);
      setAllAnimations(response.data);
      
      // If we have animations, fetch frames for the current animation type
      if (response.data.length > 0) {
        fetchFramesForAnimationType(animationType);
      }
    } catch (err) {
      console.error('Failed to fetch sprite animations:', err);
    }
  };

  const fetchFramesForAnimationType = async (type: string) => {
    setFetchingFrames(true);
    try {
      // Filter animations by the selected type
      const animationsOfType = allAnimations.filter(anim => anim.animation_type === type);
      
      if (animationsOfType.length === 0) {
        setAllFrames([]);
        setFetchingFrames(false);
        return;
      }
      
      // Fetch frames for each animation of this type
      const framesPromises = animationsOfType.map(animation => 
        axios.get(`http://localhost:8000/api/animations/${animation.id}`)
      );
      
      const responses = await Promise.all(framesPromises);
      
      // Collect all frames from all animations of this type
      let collectedFrames: any[] = [];
      responses.forEach(response => {
        if (response.data.frames && response.data.frames.length > 0) {
          // Add animation_id to each frame for reference
          const framesWithAnimationId = response.data.frames.map((frame: any) => ({
            ...frame,
            animation_id: response.data.id
          }));
          collectedFrames = [...collectedFrames, ...framesWithAnimationId];
        }
      });
      
      // Sort frames by creation date (newest first)
      collectedFrames.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
      });
      
      setAllFrames(collectedFrames);
      
      // If there are animations of this type, set the first one as active for spritesheet generation
      if (animationsOfType.length > 0) {
        setAnimationId(animationsOfType[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch frames:', err);
    } finally {
      setFetchingFrames(false);
    }
  };

  const handleAnimationTypeChange = (type: string) => {
    setActiveAnimationType(type);
    setSelectedFrames([]);
    setSpritesheetUrl('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!spriteId) {
      setError('Sprite ID is required');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Format request as application/json with properly formatted body parameters
      const response = await axios.post(
        'http://localhost:8000/api/animations/generate', 
        {
          base_sprite_id: spriteId,
          animation_type: animationType,
          num_frames: numFrames
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      setAnimationId(response.data.id);
      setAnimationUrl(response.data.url);
      
      // Update the animations list
      await fetchSpriteAnimations(spriteId);
      
      // Set the active animation type to the one just created
      setActiveAnimationType(animationType);
    } catch (err: any) {
      setError(`Failed to generate animation: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    if (spriteId) {
      navigate(`/sprites/${spriteId}`);
    } else {
      navigate('/library');
    }
  };

  const handleFrameSelection = (frameId: string) => {
    setSelectedFrames(prev => {
      if (prev.includes(frameId)) {
        return prev.filter(id => id !== frameId);
      } else {
        return [...prev, frameId];
      }
    });
  };

  const handleRemoveFrame = (frameId: string) => {
    setSelectedFrames(prev => prev.filter(id => id !== frameId));
  };

  const handleMoveFrame = (frameId: string, direction: 'up' | 'down') => {
    setSelectedFrames(prev => {
      const index = prev.indexOf(frameId);
      if (index === -1) return prev;
      
      const newOrder = [...prev];
      if (direction === 'up' && index > 0) {
        // Swap with the previous element
        [newOrder[index], newOrder[index - 1]] = [newOrder[index - 1], newOrder[index]];
      } else if (direction === 'down' && index < prev.length - 1) {
        // Swap with the next element
        [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
      }
      
      return newOrder;
    });
  };

  const handleGenerateSpritesheet = async () => {
    if (selectedFrames.length === 0) {
      setError('Please select at least one frame for the spritesheet');
      return;
    }
    
    // Need to check if all selected frames belong to the same animation
    const frameAnimations = selectedFrames.map(frameId => {
      const frame = allFrames.find(f => f.id === frameId);
      return frame?.animation_id;
    });
    
    // Check if all frames are from the same animation
    const uniqueAnimations = Array.from(new Set(frameAnimations));
    
    if (uniqueAnimations.length > 1) {
      setError('Currently, all frames must be from the same animation to generate a spritesheet. Please select frames from only one animation.');
      return;
    }
    
    // Use the animation ID of the first selected frame
    const targetAnimationId = frameAnimations[0];
    
    setSpritesheetGenerating(true);
    setError('');
    
    try {
      // First reorder the frames in the animation
      await axios.post(
        `http://localhost:8000/api/animations/frames/reorder`,
        {
          animation_id: targetAnimationId,
          frame_order: selectedFrames
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Then generate the spritesheet
      const response = await axios.post(
        `http://localhost:8000/api/animations/spritesheet/${targetAnimationId}`
      );
      
      setSpritesheetUrl(response.data.url);
    } catch (err: any) {
      setError(`Failed to generate spritesheet: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    } finally {
      setSpritesheetGenerating(false);
    }
  };

  const handleViewSpritesheet = () => {
    if (spritesheetUrl) {
      window.open(spritesheetUrl, '_blank');
    }
  };
  
  const togglePlayPause = () => {
    setIsPlaying(prev => !prev);
  };
  
  const handleFpsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAnimationFps(parseInt(e.target.value));
  };

  // Count animations by type
  const animationCounts = allAnimations.reduce((counts, animation) => {
    const type = animation.animation_type || 'unknown';
    counts[type] = (counts[type] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);

  // Get unique animation types
  const animationTypes = Object.keys(animationCounts);
  
  // Get current animation frame for preview
  const currentFrame = selectedFrames.length > 0 
    ? allFrames.find(f => f.id === selectedFrames[currentFrameIndex])
    : null;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <button 
          onClick={handleGoBack}
          className="mr-3 text-blue-500 hover:text-blue-700"
        >
          ← Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Generate Animation</h1>
      </div>
      
      {spriteImage && (
        <div className="mb-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center space-x-4">
            <img 
              src={spriteImage} 
              alt={spriteName} 
              className="w-20 h-20 object-contain bg-white p-2 rounded-md shadow"
            />
            <div>
              <h2 className="text-xl font-semibold">{spriteName}</h2>
              <p className="text-sm text-gray-600">Sprite ID: {spriteId}</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Create New Animation</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {!spriteId && (
              <div>
                <label htmlFor="spriteId" className="block text-sm font-medium text-gray-700">
                  Sprite ID
                </label>
                <input
                  type="text"
                  id="spriteId"
                  value={spriteId}
                  onChange={(e) => setSpriteId(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="Enter the sprite ID to animate"
                  required
                />
              </div>
            )}

            <div>
              <label htmlFor="animationType" className="block text-sm font-medium text-gray-700">
                Animation Type
              </label>
              <select
                id="animationType"
                value={animationType}
                onChange={(e) => setAnimationType(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="idle">Idle</option>
                <option value="walk">Walk</option>
                <option value="run">Run</option>
                <option value="jump">Jump</option>
                <option value="attack">Attack</option>
              </select>
            </div>

            <div>
              <label htmlFor="numFrames" className="block text-sm font-medium text-gray-700">
                Number of Frames
              </label>
              <input
                type="number"
                id="numFrames"
                value={numFrames}
                onChange={(e) => setNumFrames(parseInt(e.target.value))}
                min={1}
                max={24}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Generate 1-24 frames (default: 4)</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Animation'}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Create Spritesheet</h2>
          
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              Select frames below to add them to your spritesheet sequence.
            </p>
            
            {selectedFrames.length > 0 ? (
              <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-medium">Selected Frames ({selectedFrames.length})</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleGenerateSpritesheet}
                      disabled={spritesheetGenerating}
                      className="px-3 py-1 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 disabled:opacity-50"
                    >
                      {spritesheetGenerating ? 'Generating...' : 'Generate Spritesheet'}
                    </button>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-0.5">
                  {selectedFrames.map((frameId, index) => {
                    const frame = allFrames.find(f => f.id === frameId);
                    return (
                      <div key={frameId} className="relative bg-white border border-gray-200 rounded-sm group">
                        <div className="absolute -top-1 -right-1 bg-blue-500 text-white rounded-full w-2 h-2 flex items-center justify-center text-[6px] z-10">
                          {index + 1}
                        </div>
                        <div className="w-4 h-4 flex items-center justify-center">
                          <img
                            src={frame?.url}
                            alt={`Selected ${index + 1}`}
                            className="max-w-full max-h-full object-contain"
                          />
                        </div>
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <button 
                            onClick={() => handleRemoveFrame(frameId)}
                            className="bg-red-500 text-white rounded-full w-2 h-2 flex items-center justify-center text-[6px]"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {spritesheetUrl && (
                  <div className="mt-4 border-t border-gray-200 pt-4">
                    <h3 className="font-medium mb-2">Generated Spritesheet</h3>
                    <img 
                      src={spritesheetUrl} 
                      alt="Generated Spritesheet" 
                      className="w-full rounded-md border border-gray-200"
                    />
                    <div className="flex items-center justify-between mt-3">
                      <button
                        onClick={handleViewSpritesheet}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                      >
                        Open in New Tab
                      </button>
                    </div>
                    
                    {/* Animation Preview */}
                    <div className="mt-4 border-t border-gray-200 pt-4">
                      <h3 className="font-medium mb-2">Animation Preview</h3>
                      <div className="bg-gray-800 p-4 rounded-md flex items-center justify-center">
                        {currentFrame && (
                          <div className="relative w-36 h-36 flex items-center justify-center">
                            <img
                              src={currentFrame.url}
                              alt={`Animation Frame ${currentFrameIndex + 1}`}
                              className="max-w-full max-h-full object-contain"
                            />
                            <div className="absolute bottom-0 right-0 bg-black bg-opacity-70 text-white text-xs px-1 rounded">
                              {currentFrameIndex + 1}/{selectedFrames.length}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <button
                          onClick={togglePlayPause}
                          className={`px-3 py-1 ${isPlaying ? 'bg-yellow-600' : 'bg-green-600'} text-white text-sm rounded-md hover:bg-opacity-90`}
                        >
                          {isPlaying ? 'Pause' : 'Play'}
                        </button>
                        <div className="flex items-center space-x-2">
                          <label htmlFor="fps" className="text-xs text-gray-700">FPS:</label>
                          <input
                            type="range"
                            id="fps"
                            min="1"
                            max="24"
                            value={animationFps}
                            onChange={handleFpsChange}
                            className="w-24"
                          />
                          <span className="text-xs font-medium">{animationFps}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="border border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50">
                <p className="text-gray-500">No frames selected. Choose frames from below to create your spritesheet.</p>
              </div>
            )}
          </div>
          
          <div className="mt-4">
            <h3 className="font-medium mb-2">Animation Types</h3>
            <div className="flex flex-wrap gap-2">
              {animationTypes.map(type => (
                <button
                  key={type}
                  className={`px-3 py-1 rounded-full text-sm ${activeAnimationType === type 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                  onClick={() => handleAnimationTypeChange(type)}
                >
                  {type} ({animationCounts[type]})
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {fetchingFrames ? (
        <div className="mt-8 p-6 bg-white rounded-lg shadow-md flex justify-center">
          <p className="text-gray-600">Loading frames...</p>
        </div>
      ) : allFrames.length > 0 ? (
        <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Available '{activeAnimationType}' Frames</h2>
            <p className="text-sm text-gray-600">Click on frames to select them for your spritesheet</p>
          </div>
          
          <div className="animation-frames-grid">
            {allFrames.map((frame, index) => {
              // Find which animation this frame belongs to
              const animation = allAnimations.find(a => a.id === frame.animation_id);
              const animationName = animation ? animation.name : 'Unknown';
              const isSelected = selectedFrames.includes(frame.id);
              const selectionOrder = selectedFrames.indexOf(frame.id) + 1;
              
              return (
                <div 
                  key={frame.id} 
                  className={`frame-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleFrameSelection(frame.id)}
                >
                  <div className="frame-image-wrapper">
                    <img
                      src={frame.url}
                      alt={`Frame ${index + 1}`}
                      className="frame-image"
                    />
                    {isSelected && (
                      <div className="frame-number">
                        {selectionOrder}
                      </div>
                    )}
                  </div>
                  <div className="frame-details">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Frame {index + 1}</p>
                      <p className="text-xs text-gray-500">{animationName}</p>
                    </div>
                    {frame.prompt && (
                      <p className="text-xs text-gray-500 mt-1 truncate">{frame.prompt}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        activeAnimationType && !fetchingFrames && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
            <p className="text-gray-600">No frames found for animation type '{activeAnimationType}'. Generate this animation type first.</p>
          </div>
        )
      )}
    </div>
  );
};

export default AnimationGenerator; 