# 2D Animation Generator Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (React + TypeScript)"]
        UI[UI Components]
        subgraph UI_Components["UI Components"]
            SpriteGen[Sprite Generator]
            AnimGen[Animation Generator]
            Preview[Animation Preview]
            Library[Animation Library]
        end
        Router[React Router]
        API[API Client]
        Tailwind[Tailwind CSS]
    end

    subgraph Backend["Backend (Python + FastAPI)"]
        API_Routes[API Routes]
        subgraph Routes["API Routes"]
            SpriteAPI[Sprite Generation API]
            AnimAPI[Animation Generation API]
            PreviewAPI[Preview API]
            LibraryAPI[Library API]
        end
        DB[PostgreSQL Database]
        subgraph Models["Data Models"]
            SpriteModel[Sprite Model]
            AnimModel[Animation Model]
            UserModel[User Model]
        end
        Services[Business Logic]
        subgraph Services_Detail["Services"]
            SpriteService[Sprite Generation]
            AnimService[Animation Processing]
            StorageService[File Management]
        end
    end

    subgraph External["External Services"]
        AI_Model[AI Model]
        subgraph AI_Details["AI Components"]
            SpriteAI[Sprite Generation Model]
            MotionAI[Motion Prediction Model]
        end
        Storage[File Storage]
        subgraph Storage_Details["Storage"]
            SpriteStorage[Sprite Assets]
            AnimStorage[Animation Files]
            TempStorage[Temp Files]
        end
    end

    %% Connections
    UI --> Router
    UI --> Tailwind
    Router --> API
    API --> API_Routes
    API_Routes --> Models
    API_Routes --> Services
    Services --> DB
    Services --> AI_Model
    Services --> Storage

    %% Component Connections
    SpriteGen --> SpriteAPI
    AnimGen --> AnimAPI
    Preview --> PreviewAPI
    Library --> LibraryAPI

    SpriteAPI --> SpriteService
    AnimAPI --> AnimService
    PreviewAPI --> AnimService
    LibraryAPI --> StorageService

    SpriteService --> SpriteAI
    AnimService --> MotionAI
    StorageService --> Storage

    %% Styling
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px
    classDef external fill:#bfb,stroke:#333,stroke-width:2px
    classDef subgraph fill:#fff,stroke:#333,stroke-width:1px

    class Frontend frontend
    class Backend backend
    class External external
    class UI_Components, Routes, Models, Services_Detail, AI_Details, Storage_Details subgraph
```

## Component Descriptions

### Frontend
- **UI Components**
  - **Sprite Generator**: Interface for creating 2D sprites with customizable parameters
  - **Animation Generator**: Tool for generating animations from sprites
  - **Animation Preview**: Real-time preview of generated animations
  - **Animation Library**: Collection of saved animations and sprites
- **React Router**: Handles navigation between sprite generation, animation creation, and library views
- **API Client**: Manages communication with the backend using Axios
- **Tailwind CSS**: Styling framework for responsive and modern UI

### Backend
- **API Routes**
  - **Sprite Generation API**: Endpoint for sprite generation requests
  - **Animation Generation API**: Endpoint for animation creation
  - **Preview API**: Endpoint for animation preview
  - **Library API**: Endpoint for managing saved animations
- **PostgreSQL Database**: Stores user data, sprite metadata, and animation configurations
- **Data Models**
  - **Sprite Model**: Stores sprite properties and generation parameters
  - **Animation Model**: Stores animation sequences and motion data
  - **User Model**: Manages user accounts and preferences
- **Business Logic**
  - **Sprite Generation Service**: Handles sprite creation requests
  - **Animation Processing Service**: Manages animation generation and preview
  - **File Management Service**: Handles storage and retrieval of assets

### External Services
- **AI Model**
  - **Sprite Generation Model**: Neural network for generating 2D sprites
  - **Motion Prediction Model**: AI model for generating smooth animations
- **File Storage**
  - **Sprite Assets**: Storage for generated sprite images
  - **Animation Files**: Storage for completed animations
  - **Temporary Storage**: Cache for previews and intermediate files

## Data Flow
1. User interacts with the Sprite Generator or Animation Generator interface
2. Frontend sends request to appropriate API endpoint
3. Backend validates request and processes through relevant service
4. Service coordinates with AI models and storage
5. Generated assets are stored and metadata is saved to PostgreSQL
6. Results are returned to frontend
7. UI updates to show generated sprites or animations
8. User can save to library or generate new variations 