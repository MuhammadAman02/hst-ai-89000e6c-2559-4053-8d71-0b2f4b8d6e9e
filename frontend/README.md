# Minecraft Clone - Frontend

A React-based 3D voxel world game inspired by Minecraft, built with Three.js.

## Features

- 🎮 3D voxel world with block placement/destruction
- 🎯 First-person camera controls (WASD + mouse)
- 🧱 Multiple block types (grass, dirt, stone, water, wood, etc.)
- 🌍 Procedurally generated terrain with trees
- 🔗 Real-time multiplayer support via WebSocket
- 📱 Responsive design with modern UI
- ⚡ Optimized 3D rendering with shadows and lighting

## Controls

- **WASD** - Move around
- **Mouse** - Look around (click to capture mouse)
- **Left Click** - Destroy blocks
- **Right Click** - Place blocks
- **Space** - Jump
- **1-9** - Select block type from inventory
- **ESC** - Release mouse cursor

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
```

## Architecture

- **React** - UI framework
- **Three.js** - 3D rendering engine
- **TypeScript** - Type safety
- **WebSocket** - Real-time multiplayer communication

## Project Structure

```
src/
├── components/          # React components
│   ├── Game.tsx        # Main game component
│   ├── World.tsx       # 3D world management
│   ├── PlayerController.tsx # Player movement and interaction
│   └── GameUI.tsx      # UI overlay
├── services/           # External services
│   └── WebSocketManager.ts # Server communication
├── types/              # TypeScript definitions
├── constants/          # Game constants
└── App.tsx            # Root component
```

## Performance Optimization

- Efficient 3D scene management
- Optimized block rendering with instancing
- Frustum culling for distant blocks
- Shadow mapping for realistic lighting
- Responsive design for various screen sizes

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

Requires WebGL support for 3D rendering.