import React from 'react';

interface ProgressProps {
  value?: number;
  max?: number;
  className?: string;
  color?: string;
}

export const Progress: React.FC<ProgressProps> = ({ 
  value = 0, 
  max = 100, 
  className = '',
  color = 'bg-blue-600'
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div 
        className={`h-2 rounded-full transition-all duration-300 ${color}`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}; 