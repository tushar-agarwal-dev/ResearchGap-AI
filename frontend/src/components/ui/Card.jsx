export const Card = ({ children, className = '', borderVariant = '' }) => {
  const borders = {
    blue: 'border-l-4 border-blue-500',
    purple: 'border-t-4 border-purple-500',
    indigo: 'border-t-4 border-indigo-500',
    emerald: 'border-l-4 border-emerald-500',
  };

  return (
    <div className={`bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-6 shadow-xl transition-all hover:shadow-2xl hover:border-gray-700 ${borderVariant ? borders[borderVariant] : ''} ${className}`}>
      {children}
    </div>
  );
};
