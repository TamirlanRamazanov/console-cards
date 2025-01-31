import React, { useState } from 'react';
import Card from './Card';

const GameBoard: React.FC = () => {
  const [draggedCard, setDraggedCard] = useState<Card | null>(null);
  const [hoveredCardId, setHoveredCardId] = useState<string | null>(null);

  const isValidTarget = (sourceCard: Card, targetCard: Card) => {
    // Проверка возможности взаимодействия карт
    return true; // Здесь должна быть ваша логика проверки
  };

  const handleCardHover = (targetCard: Card | null) => {
    if (draggedCard && targetCard) {
      // Подсвечиваем только валидные цели
      if (isValidTarget(draggedCard, targetCard)) {
        setHoveredCardId(targetCard.id);
      }
    } else {
      setHoveredCardId(null);
    }
  };

  return (
    <div className="game-board">
      {/* Карты на столе */}
      <div className="table-area">
        {tableCards.map(card => (
          <Card
            key={card.id}
            card={card}
            isHighlighted={hoveredCardId === card.id}
            onMouseEnter={() => handleCardHover(card)}
            onMouseLeave={() => handleCardHover(null)}
          />
        ))}
      </div>

      {/* Карты в руке */}
      <div className="hand-area">
        {handCards.map(card => (
          <Card
            key={card.id}
            card={card}
            draggable
            onDragStart={() => setDraggedCard(card)}
            onDragEnd={() => setDraggedCard(null)}
          />
        ))}
      </div>
    </div>
  );
};

export default GameBoard; 