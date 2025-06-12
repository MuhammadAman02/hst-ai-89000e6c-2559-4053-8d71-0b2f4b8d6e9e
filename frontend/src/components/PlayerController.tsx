import * as THREE from 'three';
import World from './World';
import WebSocketManager from '../services/WebSocketManager';
import { Position, GameStats } from '../types';

class PlayerController {
  private camera: THREE.PerspectiveCamera;
  private world: World;
  private wsManager: WebSocketManager;
  private onStatsUpdate: (stats: Partial<GameStats>) => void;
  
  private velocity = new THREE.Vector3();
  private direction = new THREE.Vector3();
  private raycaster = new THREE.Raycaster();
  
  private moveForward = false;
  private moveBackward = false;
  private moveLeft = false;
  private moveRight = false;
  private canJump = false;
  private isPointerLocked = false;
  
  private stats: GameStats = {
    blocksPlaced: 0,
    blocksDestroyed: 0,
    position: { x: 0, y: 20, z: 0 },
    playersOnline: 1
  };

  constructor(
    camera: THREE.PerspectiveCamera,
    world: World,
    wsManager: WebSocketManager,
    onStatsUpdate: (stats: Partial<GameStats>) => void
  ) {
    this.camera = camera;
    this.world = world;
    this.wsManager = wsManager;
    this.onStatsUpdate = onStatsUpdate;
    
    this.setupControls();
    this.setupPointerLock();
  }

  private setupControls() {
    const onKeyDown = (event: KeyboardEvent) => {
      switch (event.code) {
        case 'ArrowUp':
        case 'KeyW':
          this.moveForward = true;
          break;
        case 'ArrowLeft':
        case 'KeyA':
          this.moveLeft = true;
          break;
        case 'ArrowDown':
        case 'KeyS':
          this.moveBackward = true;
          break;
        case 'ArrowRight':
        case 'KeyD':
          this.moveRight = true;
          break;
        case 'Space':
          if (this.canJump) this.velocity.y += 10;
          break;
      }
    };

    const onKeyUp = (event: KeyboardEvent) => {
      switch (event.code) {
        case 'ArrowUp':
        case 'KeyW':
          this.moveForward = false;
          break;
        case 'ArrowLeft':
        case 'KeyA':
          this.moveLeft = false;
          break;
        case 'ArrowDown':
        case 'KeyS':
          this.moveBackward = false;
          break;
        case 'ArrowRight':
        case 'KeyD':
          this.moveRight = false;
          break;
      }
    };

    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keyup', onKeyUp);
  }

  private setupPointerLock() {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const onMouseMove = (event: MouseEvent) => {
      if (!this.isPointerLocked) return;

      const movementX = event.movementX || 0;
      const movementY = event.movementY || 0;

      this.camera.rotation.y -= movementX * 0.002;
      this.camera.rotation.x -= movementY * 0.002;
      this.camera.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.camera.rotation.x));
    };

    const onPointerLockChange = () => {
      this.isPointerLocked = document.pointerLockElement === canvas;
    };

    canvas.addEventListener('click', () => {
      if (!this.isPointerLocked) {
        canvas.requestPointerLock();
      }
    });

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('pointerlockchange', onPointerLockChange);
  }

  update() {
    const delta = 0.016; // Assume 60fps

    // Update movement
    this.velocity.x -= this.velocity.x * 10.0 * delta;
    this.velocity.z -= this.velocity.z * 10.0 * delta;
    this.velocity.y -= 9.8 * 10.0 * delta; // Gravity

    this.direction.z = Number(this.moveForward) - Number(this.moveBackward);
    this.direction.x = Number(this.moveRight) - Number(this.moveLeft);
    this.direction.normalize();

    if (this.moveForward || this.moveBackward) {
      this.velocity.z -= this.direction.z * 400.0 * delta;
    }
    if (this.moveLeft || this.moveRight) {
      this.velocity.x -= this.direction.x * 400.0 * delta;
    }

    // Apply movement
    const oldPosition = this.camera.position.clone();
    this.camera.position.add(this.velocity.clone().multiplyScalar(delta));

    // Simple collision detection
    const playerHeight = 1.8;
    const groundY = this.getGroundHeight(this.camera.position.x, this.camera.position.z) + playerHeight;
    
    if (this.camera.position.y <= groundY) {
      this.camera.position.y = groundY;
      this.velocity.y = 0;
      this.canJump = true;
    } else {
      this.canJump = false;
    }

    // Update stats
    this.stats.position = {
      x: Math.round(this.camera.position.x * 10) / 10,
      y: Math.round(this.camera.position.y * 10) / 10,
      z: Math.round(this.camera.position.z * 10) / 10
    };
    
    this.onStatsUpdate(this.stats);
  }

  private getGroundHeight(x: number, z: number): number {
    // Simple ground height calculation
    // In a real implementation, this would check the world's block data
    return 10; // Simplified ground level
  }

  placeBlock(blockType: number) {
    this.raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);
    const hit = this.world.raycast(this.raycaster);
    
    if (hit) {
      const placePosition = {
        x: hit.position.x + hit.normal.x,
        y: hit.position.y + hit.normal.y,
        z: hit.position.z + hit.normal.z
      };
      
      if (this.world.placeBlock(placePosition, blockType)) {
        this.stats.blocksPlaced++;
        this.wsManager.sendBlockUpdate(placePosition, blockType);
      }
    }
  }

  destroyBlock() {
    this.raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);
    const hit = this.world.raycast(this.raycaster);
    
    if (hit) {
      if (this.world.removeBlock(hit.position)) {
        this.stats.blocksDestroyed++;
        this.wsManager.sendBlockUpdate(hit.position, 0);
      }
    }
  }

  setPointerLock(enabled: boolean) {
    this.isPointerLocked = enabled;
  }
}

export default PlayerController;