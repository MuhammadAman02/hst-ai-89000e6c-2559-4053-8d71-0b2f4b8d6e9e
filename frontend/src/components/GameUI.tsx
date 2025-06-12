import React from 'react';
import { INVENTORY_BLOCKS } from '../constants/blocks';
import { GameStats } from '../types';

interface GameUIProps {
  selectedBlockType: number;
  onBlockSelect: (blockType: number) => void;
  gameStats: GameStats;
  isConnected: boolean;
}

const GameUI: React.FC<GameUIProps> = ({
  selectedBlockType,
  onBlockSelect,
  gameStats,
  isConnected
}) => {
  return (
    <div className="ui-overlay">
      {/* Crosshair */}
      <div className="crosshair" />
      
      {/* Game Info */}
      <div className="game-info">
        <div>Position: {gameStats.position.x.toFixed(1)}, {gameStats.position.y.toFixed(1)}, {gameStats.position.z.toFixed(1)}</div>
        <div>Blocks Placed: {gameStats.blocksPlaced}</div>
        <div>Blocks Destroyed: {gameStats.blocksDestroyed}</div>
        <div>Players Online: {gameStats.playersOnline}</div>
        <div>Status: {isConnected ? '🟢 Connected' : '🔴 Offline'}</div>
      </div>
      
      {/* Controls Info */}
      <div className="controls-info">
        <div><strong>Controls:</strong></div>
        <div>WASD - Move</div>
        <div>Mouse - Look</div>
        <div>Left Click - Destroy</div>
        <div>Right Click - Place</div>
        <div>Space - Jump</div>
        <div>1-9 - Select Block</div>
        <div>Click to capture mouse</div>
      </div>
      
      {/* Inventory Bar */}
      <div className="inventory-bar">
        {INVENTORY_BLOCKS.map((block, index) => (
          <div
            key={block.id}
            className={`inventory-slot ${selectedBlockType === block.id ? 'selected' : ''}`}
            onClick={() => onBlockSelect(block.id)}
            title={`${block.name} (${index + 1})`}
          >
            <div
              className="block-preview"
              style={{ backgroundColor: block.color }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameUI;