import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { BlockType, Position, GameStats, WorldState } from '../types';
import { BLOCK_TYPES, INVENTORY_BLOCKS } from '../constants/blocks';
import World from './World';
import PlayerController from './PlayerController';
import GameUI from './GameUI';
import WebSocketManager from '../services/WebSocketManager';

const Game: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const worldRef = useRef<World>();
  const playerControllerRef = useRef<PlayerController>();
  const wsManagerRef = useRef<WebSocketManager>();
  const animationIdRef = useRef<number>();
  
  const [selectedBlockType, setSelectedBlockType] = useState<number>(1);
  const [gameStats, setGameStats] = useState<GameStats>({
    blocksPlaced: 0,
    blocksDestroyed: 0,
    position: { x: 0, y: 20, z: 0 },
    playersOnline: 1
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  const handleWorldUpdate = useCallback((worldState: WorldState) => {
    if (worldRef.current) {
      worldRef.current.updateFromState(worldState);
    }
  }, []);

  const handleStatsUpdate = useCallback((stats: Partial<GameStats>) => {
    setGameStats(prev => ({ ...prev, ...stats }));
  }, []);

  useEffect(() => {
    if (!mountRef.current) return;

    console.log('Initializing Minecraft-like game...');
    setIsLoading(true);

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb); // Sky blue
    scene.fog = new THREE.Fog(0x87ceeb, 50, 200);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(0, 20, 0);
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.setClearColor(0x87ceeb);
    rendererRef.current = renderer;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 500;
    directionalLight.shadow.camera.left = -100;
    directionalLight.shadow.camera.right = 100;
    directionalLight.shadow.camera.top = 100;
    directionalLight.shadow.camera.bottom = -100;
    scene.add(directionalLight);

    // Initialize world
    const world = new World(scene);
    worldRef.current = world;

    // Initialize WebSocket manager
    const wsManager = new WebSocketManager();
    wsManagerRef.current = wsManager;

    wsManager.onWorldUpdate = handleWorldUpdate;
    wsManager.onStatsUpdate = handleStatsUpdate;
    wsManager.onConnectionChange = setIsConnected;

    // Initialize player controller
    const playerController = new PlayerController(
      camera,
      world,
      wsManager,
      handleStatsUpdate
    );
    playerControllerRef.current = playerController;

    // Handle block placement/destruction
    const handleClick = (event: MouseEvent) => {
      if (!playerController) return;
      
      if (event.button === 0) { // Left click - destroy
        playerController.destroyBlock();
      } else if (event.button === 2) { // Right click - place
        playerController.placeBlock(selectedBlockType);
      }
    };

    const handleContextMenu = (event: MouseEvent) => {
      event.preventDefault();
    };

    // Handle keyboard input for block selection
    const handleKeyDown = (event: KeyboardEvent) => {
      const key = parseInt(event.key);
      if (key >= 1 && key <= INVENTORY_BLOCKS.length) {
        setSelectedBlockType(key);
      }
    };

    mountRef.current.appendChild(renderer.domElement);
    renderer.domElement.addEventListener('click', handleClick);
    renderer.domElement.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      
      if (playerController) {
        playerController.update();
      }
      
      renderer.render(scene, camera);
    };

    // Start connection and animation
    wsManager.connect().then(() => {
      setIsLoading(false);
      animate();
    }).catch((error) => {
      console.error('Failed to connect to server:', error);
      setIsLoading(false);
      animate(); // Start anyway for offline mode
    });

    // Handle window resize
    const handleResize = () => {
      if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('keydown', handleKeyDown);
      
      if (wsManagerRef.current) {
        wsManagerRef.current.disconnect();
      }
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      
      renderer.dispose();
    };
  }, [selectedBlockType, handleWorldUpdate, handleStatsUpdate]);

  const handleBlockSelect = (blockType: number) => {
    setSelectedBlockType(blockType);
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <div>Loading Minecraft World...</div>
        <div style={{ fontSize: '14px', marginTop: '10px' }}>
          Connecting to server...
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      <div ref={mountRef} className="w-full h-full" />
      
      <GameUI
        selectedBlockType={selectedBlockType}
        onBlockSelect={handleBlockSelect}
        gameStats={gameStats}
        isConnected={isConnected}
      />
    </div>
  );
};

export default Game;