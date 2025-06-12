import { BlockType } from '../types';

export const BLOCK_TYPES: BlockType[] = [
  { id: 0, name: 'Air', color: '#000000' },
  { id: 1, name: 'Grass', color: '#4a7c59' },
  { id: 2, name: 'Dirt', color: '#8b4513' },
  { id: 3, name: 'Stone', color: '#696969' },
  { id: 4, name: 'Water', color: '#4169e1' },
  { id: 5, name: 'Wood', color: '#deb887' },
  { id: 6, name: 'Sand', color: '#f4a460' },
  { id: 7, name: 'Cobblestone', color: '#778899' },
  { id: 8, name: 'Brick', color: '#b22222' },
];

export const INVENTORY_BLOCKS = BLOCK_TYPES.slice(1); // Exclude air