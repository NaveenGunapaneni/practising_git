import React from 'react';
import { clsx } from 'clsx';

const Card = ({ 
  children, 
  className = '', 
  padding = 'default',
  ...props 
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    default: 'p-6',
    lg: 'p-8'
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-lg shadow-sm border border-gray-200',
        paddingClasses[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
