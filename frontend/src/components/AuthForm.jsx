import { useState } from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';

export const AuthForm = ({ onAuth, isLoading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e, mode) => {
    e.preventDefault();
    onAuth(mode, email, password);
  };

  return (
    <Card borderVariant="blue" className="max-w-md mx-auto">
      <div className="space-y-6">
        <header className="text-center">
          <h2 className="text-2xl font-black text-white uppercase tracking-tight">Access Platform</h2>
          <p className="text-sm text-gray-500 mt-1 uppercase font-bold tracking-widest text-[10px]">Secure Researcher Login</p>
        </header>

        <form className="space-y-4">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Work Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@university.edu" 
              className="w-full bg-black/40 border border-gray-800 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 text-white rounded-xl px-4 py-3 outline-none transition-all placeholder:text-gray-700"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e, 'login')}
              placeholder="••••••••" 
              className="w-full bg-black/40 border border-gray-800 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 text-white rounded-xl px-4 py-3 outline-none transition-all placeholder:text-gray-700"
            />
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <Button variant="secondary" onClick={(e) => handleSubmit(e, 'signup')} disabled={isLoading}>
              {isLoading ? '...' : 'Create Account'}
            </Button>
            <Button variant="primary" onClick={(e) => handleSubmit(e, 'login')} disabled={isLoading}>
              {isLoading ? '...' : 'Sign In'}
            </Button>
          </div>
        </form>
        
        <footer className="pt-4 border-t border-gray-800/50 flex flex-col items-center gap-2">
          <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest text-center">
            Session-based Intelligence • Stateless Analysis
          </p>
        </footer>
      </div>
    </Card>
  );
};
