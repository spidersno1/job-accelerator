import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'outline';
  style?: React.CSSProperties;
  onClick?: () => void;
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  className = '',
  variant = 'default',
  style,
  onClick
}) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    secondary: 'bg-gray-600 text-white',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    outline: 'border border-gray-300 bg-white text-gray-700'
  };

  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
      style={style}
      onClick={onClick}
    >
      {children}
    </span>
  );
}; 