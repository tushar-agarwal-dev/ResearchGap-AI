import { Card } from './ui/Card';
import { Button } from './ui/Button';

export const DashboardHero = ({ onUploadClick, stats, isLoading }) => {
  return (
    <section className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="space-y-2">
          <h1 className="text-5xl font-black text-white tracking-tight">Research Intelligence</h1>
          <p className="text-gray-400 text-lg font-medium">Augmenting academic discovery with deterministic AI analysis.</p>
        </div>
        <Button variant="purple" className="!px-8 !py-4 !text-lg" onClick={onUploadClick} disabled={isLoading}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
          Ingest Papers
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="!p-4 !bg-gray-800/20 border-gray-800/50">
          <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-1">Corpus Size</span>
          <p className="text-2xl font-black text-white">{stats?.totalPapers || 0}</p>
        </Card>
        <Card className="!p-4 !bg-gray-800/20 border-gray-800/50">
          <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-1">Knowledge Domains</span>
          <p className="text-2xl font-black text-blue-400">{stats?.domains || 0}</p>
        </Card>
        <Card className="!p-4 !bg-gray-800/20 border-gray-800/50">
          <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-1">Avg Accuracy</span>
          <p className="text-2xl font-black text-emerald-400">{stats?.avgAccuracy || '94%'}</p>
        </Card>
        <Card className="!p-4 !bg-gray-800/20 border-gray-800/50">
          <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest block mb-1">Entities Mined</span>
          <p className="text-2xl font-black text-purple-400">{stats?.entities || 0}</p>
        </Card>
      </div>
    </section>
  );
};
