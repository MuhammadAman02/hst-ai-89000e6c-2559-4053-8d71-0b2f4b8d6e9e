# Minecraft Clone - Full Stack Application

A full-stack Minecraft-like voxel world game with React frontend and Python FastAPI backend, featuring real-time multiplayer support.

## 🎮 Features

### Frontend (React + Three.js)
- **3D Voxel World**: Fully interactive 3D block-based environment
- **First-Person Controls**: WASD movement with mouse look
- **Block System**: 8 different block types (grass, dirt, stone, water, wood, sand, cobblestone, brick)
- **Real-time Multiplayer**: See other players in real-time
- **Modern UI**: Clean, Minecraft-inspired interface
- **Responsive Design**: Works on desktop and mobile devices

### Backend (Python FastAPI)
- **Real-time Communication**: WebSocket support for instant updates
- **World Persistence**: Automatic world saving and loading
- **Player Management**: Multi-player session handling
- **RESTful API**: Complete REST API for world data
- **Performance Optimized**: Efficient world state management
- **Production Ready**: Docker containerization and deployment

## 🚀 Quick Start

### Prerequisites
- **Frontend**: Node.js 16+, npm/yarn
- **Backend**: Python 3.10+, pip
- **Deployment**: Docker (optional)

### Development Setup

#### 1. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```
The backend will be available at `http://localhost:8000`

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```
The frontend will be available at `http://localhost:3000`

### Production Deployment

#### Docker Deployment
```bash
# Build and run with Docker
docker build -t minecraft-clone .
docker run -p 8000:8000 minecraft-clone
```

#### Fly.io Deployment
```bash
# Deploy to Fly.io
fly deploy
```

## 🎯 How to Play

### Controls
- **WASD** - Move around the world
- **Mouse** - Look around (click to capture cursor)
- **Left Click** - Destroy blocks
- **Right Click** - Place blocks
- **Space** - Jump
- **1-8** - Select block type from inventory
- **ESC** - Release mouse cursor

### Gameplay
1. **Explore**: Navigate the procedurally generated world
2. **Build**: Place blocks to create structures
3. **Destroy**: Remove blocks to reshape the terrain
4. **Multiplayer**: See other players building in real-time

## 🏗️ Architecture

### Frontend Architecture
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Game.tsx        # Main game orchestrator
│   │   ├── World.tsx       # 3D world management
│   │   ├── PlayerController.tsx # Player input/movement
│   │   └── GameUI.tsx      # UI overlay
│   ├── services/           # External services
│   │   └── WebSocketManager.ts # Real-time communication
│   ├── types/              # TypeScript definitions
│   └── constants/          # Game constants
```

### Backend Architecture
```
backend/
├── app/
│   ├── models/             # Data models (Pydantic)
│   ├── services/           # Business logic
│   │   ├── world_manager.py    # World state management
│   │   └── connection_manager.py # WebSocket connections
│   └── main.py            # FastAPI application
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## 🔧 Technical Details

### Frontend Technologies
- **React 18** - UI framework
- **Three.js** - 3D rendering engine
- **TypeScript** - Type safety
- **WebSocket** - Real-time communication

### Backend Technologies
- **FastAPI** - Modern Python web framework
- **WebSockets** - Real-time bidirectional communication
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

### Key Features Implementation

#### 3D World Rendering
- Efficient block rendering with Three.js
- Optimized geometry instancing
- Shadow mapping and lighting
- Frustum culling for performance

#### Real-time Multiplayer
- WebSocket-based communication
- Efficient state synchronization
- Player position broadcasting
- Block update propagation

#### World Persistence
- JSON-based world storage
- Automatic periodic saving
- World state recovery on restart
- Player session management

## 📊 Performance

### Optimization Features
- **Frontend**: Efficient 3D rendering, object pooling, frustum culling
- **Backend**: Async operations, connection pooling, efficient data structures
- **Network**: Minimal data transfer, delta updates, compression

### Scalability
- Supports up to 50 concurrent players
- Efficient memory usage
- Horizontal scaling ready
- Database integration ready

## 🔒 Security

### Security Features
- Input validation on all endpoints
- CORS protection
- Rate limiting
- Secure WebSocket connections
- Environment-based configuration

## 🚀 Deployment

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# World Settings
WORLD_SIZE=100
MAX_HEIGHT=50
AUTO_SAVE_INTERVAL=300

# Player Settings
MAX_PLAYERS=50
PLAYER_TIMEOUT=300
```

### Health Checks
- `/health` - Backend health status
- `/api/stats` - Game statistics
- WebSocket connection monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] Enhanced terrain generation
- [ ] More block types and tools
- [ ] Player authentication
- [ ] World sharing and persistence
- [ ] Mobile app version
- [ ] VR support

---

**Built with ❤️ using React, Three.js, Python, and FastAPI**