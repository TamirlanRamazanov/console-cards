interface CardProps {
  card: Card;
  isHighlighted?: boolean;
}

const Card: React.FC<CardProps> = ({ card, isHighlighted, ...props }) => {
  return (
    <div 
      className={`card ${isHighlighted ? 'card-highlighted' : ''}`}
      {...props}
    >
      {/* содержимое карты */}
    </div>
  );
}; 