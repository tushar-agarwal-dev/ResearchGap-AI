import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

export const PaperSnapshot = ({ paper, onSelect }) => {
  const { insights, filename, summary } = paper;
  
  return (
    <Card className="flex flex-col h-full group">
      <div className="flex justify-between items-start mb-4">
        <Badge variant="indigo">{insights?.domain || 'General'}</Badge>
        <span className="text-[10px] font-bold text-gray-500 font-mono">ID: {paper.id}</span>
      </div>

      <h3 className="text-xl font-black text-white group-hover:text-blue-400 transition-colors line-clamp-2 mb-2">
        {filename}
      </h3>
      
      <p className="text-gray-400 text-sm leading-relaxed line-clamp-3 mb-6 flex-1">
        {summary || 'No summary available for this document.'}
      </p>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="space-y-1">
          <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest block">Methodology</span>
          <p className="text-xs text-gray-200 font-bold truncate">{(insights?.algorithms || []).join(', ') || 'N/A'}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest block">Performance</span>
          <p className="text-xs text-emerald-400 font-black truncate">{insights?.results?.metrics?.accuracy || 'N/A'}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest block">Complexity</span>
          <Badge variant={insights?.complexity === 'Advanced' ? 'danger' : 'success'} className="!text-[8px]">
            {insights?.complexity || 'Intermediate'}
          </Badge>
        </div>
        <div className="space-y-1">
          <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest block">Read Time</span>
          <p className="text-xs text-blue-400 font-bold">{insights?.reading_time || 10} min</p>
        </div>
      </div>

      <Button variant="ghost" className="w-full !justify-between !px-2 border-t border-gray-800 rounded-none pt-4" onClick={() => onSelect(paper)}>
        <span className="text-[10px] font-black uppercase tracking-widest">Full Intelligence Report</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
      </Button>
    </Card>
  );
};
