import * as THREE from 'three';
import { BLOCK_TYPES } from '../constants/blocks';
import { WorldState, Block, Position } from '../types';

class World {
  private scene: THREE.Scene;
  private blocks: Map<string, THREE.Mesh> = new Map();
  private blockGeometry: THREE.BoxGeometry;
  private materials: THREE.MeshLambertMaterial[] = [];

  constructor(scene: THREE.Scene) {
    this.scene = scene;
    this.blockGeometry = new THREE.BoxGeometry(1, 1, 1);
    
    // Create materials for each block type
    BLOCK_TYPES.forEach(blockType => {
      const material = new THREE.MeshLambertMaterial({ 
        color: blockType.color,
        transparent: blockType.id === 4, // Water is transparent
        opacity: blockType.id === 4 ? 0.7 : 1.0
      });
      this.materials[blockType.id] = material;
    });

    this.generateInitialTerrain();
  }

  private generateInitialTerrain() {
    // Generate a simple flat terrain with some hills
    const size = 20;
    const centerX = 0;
    const centerZ = 0;

    for (let x = -size; x <= size; x++) {
      for (let z = -size; z <= size; z++) {
        // Create height variation using simple noise
        const distance = Math.sqrt(x * x + z * z);
        const height = Math.max(0, Math.floor(5 - distance * 0.2 + Math.sin(x * 0.3) * 2 + Math.cos(z * 0.3) * 2));
        
        for (let y = 0; y <= height; y++) {
          let blockType = 3; // Stone
          
          if (y === height && height > 2) {
            blockType = 1; // Grass on top
          } else if (y === height && height <= 2) {
            blockType = 6; // Sand near water level
          } else if (y >= height - 2 && height > 2) {
            blockType = 2; // Dirt below grass
          }
          
          this.placeBlock({ x: centerX + x, y, z: centerZ + z }, blockType);
        }
        
        // Add some water at low levels
        if (height <= 2) {
          for (let y = height + 1; y <= 3; y++) {
            this.placeBlock({ x: centerX + x, y, z: centerZ + z }, 4); // Water
          }
        }
      }
    }

    // Add some trees
    this.generateTrees();
  }

  private generateTrees() {
    const treePositions = [
      { x: 5, z: 5 },
      { x: -8, z: 3 },
      { x: 12, z: -7 },
      { x: -15, z: -12 },
      { x: 8, z: -15 }
    ];

    treePositions.forEach(pos => {
      const groundHeight = this.getGroundHeight(pos.x, pos.z);
      if (groundHeight > 3) { // Only place trees on grass, not in water
        // Tree trunk
        for (let y = groundHeight + 1; y <= groundHeight + 4; y++) {
          this.placeBlock({ x: pos.x, y, z: pos.z }, 5); // Wood
        }
        
        // Tree leaves
        for (let x = pos.x - 2; x <= pos.x + 2; x++) {
          for (let z = pos.z - 2; z <= pos.z + 2; z++) {
            for (let y = groundHeight + 3; y <= groundHeight + 6; y++) {
              if (Math.abs(x - pos.x) + Math.abs(z - pos.z) + Math.abs(y - (groundHeight + 4)) <= 3) {
                if (!(x === pos.x && z === pos.z && y <= groundHeight + 4)) {
                  this.placeBlock({ x, y, z }, 1); // Grass/leaves
                }
              }
            }
          }
        }
      }
    });
  }

  private getGroundHeight(x: number, z: number): number {
    for (let y = 20; y >= 0; y--) {
      const key = `${x},${y},${z}`;
      if (this.blocks.has(key)) {
        return y;
      }
    }
    return 0;
  }

  private positionToKey(position: Position): string {
    return `${Math.floor(position.x)},${Math.floor(position.y)},${Math.floor(position.z)}`;
  }

  placeBlock(position: Position, blockType: number): boolean {
    if (blockType === 0) return this.removeBlock(position);
    
    const key = this.positionToKey(position);
    
    // Remove existing block if present
    this.removeBlock(position);
    
    // Create new block
    const mesh = new THREE.Mesh(this.blockGeometry, this.materials[blockType]);
    mesh.position.set(
      Math.floor(position.x) + 0.5,
      Math.floor(position.y) + 0.5,
      Math.floor(position.z) + 0.5
    );
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    this.scene.add(mesh);
    this.blocks.set(key, mesh);
    
    return true;
  }

  removeBlock(position: Position): boolean {
    const key = this.positionToKey(position);
    const mesh = this.blocks.get(key);
    
    if (mesh) {
      this.scene.remove(mesh);
      this.blocks.delete(key);
      return true;
    }
    
    return false;
  }

  getBlockAt(position: Position): number {
    const key = this.positionToKey(position);
    return this.blocks.has(key) ? 1 : 0; // Simplified - return 1 if block exists, 0 if not
  }

  raycast(raycaster: THREE.Raycaster): { position: Position; normal: THREE.Vector3 } | null {
    const intersects = raycaster.intersectObjects(Array.from(this.blocks.values()));
    
    if (intersects.length > 0) {
      const intersect = intersects[0];
      const position = intersect.point.clone().add(intersect.face!.normal.clone().multiplyScalar(-0.5));
      
      return {
        position: {
          x: Math.floor(position.x),
          y: Math.floor(position.y),
          z: Math.floor(position.z)
        },
        normal: intersect.face!.normal
      };
    }
    
    return null;
  }

  updateFromState(worldState: WorldState) {
    // Update world based on server state
    // This would be used for multiplayer synchronization
    worldState.blocks.forEach(block => {
      this.placeBlock(block.position, block.type);
    });
  }

  getWorldState(): WorldState {
    const blocks: Block[] = [];
    this.blocks.forEach((mesh, key) => {
      const [x, y, z] = key.split(',').map(Number);
      blocks.push({
        position: { x, y, z },
        type: 1 // Simplified - would need to track actual block types
      });
    });

    return {
      blocks,
      players: []
    };
  }
}

export default World;