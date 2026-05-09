export const Button = ({ children, onClick, variant = 'primary', disabled = false, className = '', type = 'button' }) => {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20',
    secondary: 'bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700',
    success: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-600/20',
    danger: 'bg-red-600/20 text-red-400 border border-red-600/50 hover:bg-red-600 hover:text-white',
    purple: 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-600/20',
    ghost: 'bg-transparent hover:bg-gray-800 text-gray-400 hover:text-white',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-xl font-bold transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};
