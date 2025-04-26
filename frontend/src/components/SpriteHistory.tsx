import React from 'react';

// Define the type for a sprite version
export interface SpriteVersion {
  id: string;
  imageUrl: string;
  prompt: string;
  createdAt: string;
}

interface SpriteHistoryProps {
  versions: SpriteVersion[];
  currentVersionId: string;
  onSelectVersion: (version: SpriteVersion) => void;
}

const SpriteHistory: React.FC<SpriteHistoryProps> = ({
  versions,
  currentVersionId,
  onSelectVersion,
}) => {
  // Helper function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    }).format(date);
  };

  // Sort versions by date (newest first)
  const sortedVersions = [...versions].sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  return (
    <div className="sprite-history">
      <h3 className="history-title">Sprite History</h3>
      
      {versions.length === 0 ? (
        <div className="empty-history">No previous versions available</div>
      ) : (
        <div className="timeline">
          {sortedVersions.map((version, index) => {
            const isCurrentVersion = version.id === currentVersionId;
            const isLastItem = index === sortedVersions.length - 1;
            
            return (
              <div 
                key={version.id}
                className={`timeline-item ${isCurrentVersion ? 'current' : ''}`}
                onClick={() => onSelectVersion(version)}
              >
                <div className="timeline-connector">
                  <div className="timeline-dot"></div>
                  {!isLastItem && <div className="timeline-line"></div>}
                </div>
                
                <div className="timeline-content">
                  <div className="timeline-image">
                    <img src={version.imageUrl} alt="Sprite version" />
                  </div>
                  
                  <div className="timeline-info">
                    <span className="timeline-date">
                      {formatDate(version.createdAt)}
                    </span>
                    <p className="timeline-prompt">{version.prompt}</p>
                    {isCurrentVersion && (
                      <span className="current-version-badge">Current</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SpriteHistory; 