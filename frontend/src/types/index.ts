export interface BlockType {
  id: number;
  name: string;
  color: string;
  texture?: string;
}

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface Block {
  position: Position;
  type: number;
}

export interface Player {
  id: string;
  position: Position;
  rotation: Position;
}

export interface WorldState {
  blocks: Block[];
  players: Player[];
}

export interface GameStats {
  blocksPlaced: number;
  blocksDestroyed: number;
  position: Position;
  playersOnline: number;
}