import React from 'react';

interface InputProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyPress?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  type?: string;
  disabled?: boolean;
  name?: string;
  id?: string;
}

export const Input: React.FC<InputProps> = ({ 
  value, 
  onChange, 
  onKeyPress,
  placeholder, 
  className = '',
  type = 'text',
  disabled = false,
  name,
  id
}) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      onKeyPress={onKeyPress}
      placeholder={placeholder}
      disabled={disabled}
      name={name}
      id={id}
      className={`block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500 ${className}`}
    />
  );
}; 