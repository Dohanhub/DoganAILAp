import React from 'react';

type Size = 'sm' | 'md' | 'lg';

const sizeMap: Record<Size, string> = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-10 w-10',
};

export const LoadingSpinner: React.FC<{ size?: Size }> = ({ size = 'md' }) => {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`inline-block animate-spin rounded-full border-2 border-gray-300 border-t-green-600 ${sizeMap[size]}`}
    />
  );
};

export default LoadingSpinner;

