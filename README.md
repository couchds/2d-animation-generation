# 2D Animation Generator

A full-stack application for generating and managing 2D sprites and animations using AI.

## System Architecture

### Overview
The application follows a modern full-stack architecture with a clear separation between frontend and backend components:

```
2D Animation Generator
├── Frontend (React + TypeScript)
│   ├── UI Components
│   ├── API Services
│   └── State Management
└── Backend (FastAPI + Python)
    ├── API Layer
    ├── Service Layer
    ├── Data Layer
    └── AI Integration
```

### Frontend Architecture
- **Framework**: React with TypeScript
- **UI Library**: Tailwind CSS for styling
- **Routing**: React Router for navigation
- **State Management**: React Hooks (useState, useEffect)
- **API Integration**: Axios for HTTP requests
- **Build Tool**: Vite for fast development and building

Key Components:
- `App.tsx`: Main application component with routing
- `Navbar.tsx`: Navigation component
- `Home.tsx`: Landing page
- `SpriteGenerator.tsx`: Base sprite generation interface
- `AnimationGenerator.tsx`: Animation generation interface
- API Services: `spriteService.ts` and `animationService.ts`

### Backend Architecture
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: OpenAI's DALL-E API
- **API Documentation**: Automatic OpenAPI/Swagger docs

Layers:
1. **API Layer** (`/api/endpoints/`)
   - RESTful endpoints for sprites and animations
   - Request/response models with Pydantic
   - Error handling and validation

2. **Service Layer** (`/services/`)
   - Business logic implementation
   - AI integration with OpenAI
   - Data processing and transformation

3. **Data Layer** (`/models/`)
   - SQLAlchemy models for database entities
   - Relationships between sprites and animations
   - Database session management

4. **Utility Layer** (`/utils/`)
   - Database connection management
   - Common helper functions
   - Configuration handling

### Data Flow
1. User interacts with frontend interface
2. Frontend makes API calls to backend
3. Backend processes request and calls OpenAI API
4. Generated images are stored in database
5. Response sent back to frontend
6. Frontend displays results to user

### API Endpoints
- `POST /api/sprites/generate`: Generate new sprite
- `GET /api/sprites/{sprite_id}`: Get specific sprite
- `POST /api/animations/generate`: Generate new animation
- `GET /api/animations/{animation_id}`: Get specific animation
- `GET /api/animations/sprite/{sprite_id}`: Get all animations for a sprite

### Database Schema
```sql
CREATE TABLE sprites (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE animations (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    animation_type TEXT NOT NULL,
    base_sprite_id TEXT NOT NULL,
    FOREIGN KEY (base_sprite_id) REFERENCES sprites(id)
);
```

## Setup Instructions

### Backend Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. Initialize database:
   ```bash
   # From the backend directory
   ./scripts/init_db.sh
   ```

5. Run backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

## Development
- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:3000`
- API documentation available at `http://localhost:8000/docs`

## Features
- Generate base sprites from text descriptions
- Create animation variations (idle, walk, run, etc.)
- View and manage generated sprites and animations
- Build custom spritesheets

## Future Enhancements
- [ ] Sprite editing capabilities
- [ ] Animation sequence editor
- [ ] Custom animation types
- [ ] Batch generation
- [ ] Export options for different formats
- [ ] User authentication and sprite management
- [ ] Collaboration features

## Database Configuration

The application uses SQLite by default, but can be configured to use other databases like PostgreSQL or MySQL.

### Default Configuration (SQLite)
The default configuration uses SQLite with the following settings:
- Database file: `sprites.db`
- Location: Backend directory
- No authentication required

### Alternative Database Setup
To use a different database:

1. Update `.env` file with your database credentials:
   ```bash
   DB_TYPE=postgresql  # or mysql
   DB_HOST=localhost
   DB_PORT=5432       # 3306 for MySQL
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=sprites_db
   ```

2. Install the appropriate database driver:
   ```bash
   # For PostgreSQL
   pip install psycopg2-binary
   
   # For MySQL
   pip install mysqlclient
   ```

3. Create the database:
   ```bash
   # PostgreSQL
   createdb sprites_db
   
   # MySQL
   mysql -u root -p -e "CREATE DATABASE sprites_db;"
   ```

4. Run the initialization script:
   ```bash
   ./scripts/init_db.sh
   ```
