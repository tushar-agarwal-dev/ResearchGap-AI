import { Badge } from './ui/Badge';
import { Card } from './ui/Card';

export const ProductInfoPanel = ({ stats }) => {
  return (
    <div className="space-y-8 sticky top-32">
      <section className="space-y-4">
        <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Platform Intelligence</h3>
        <Card className="!p-6 bg-gradient-to-br from-blue-600/10 to-transparent border-blue-500/20">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-blue-600/20 rounded-2xl flex items-center justify-center text-blue-500 shadow-inner">
               <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="m4.93 4.93 14.14 14.14"/><path d="M2 12h20"/><path d="m4.93 19.07 14.14-14.14"/></svg>
            </div>
            <div>
              <h4 className="text-sm font-black text-white uppercase">ResearchGap Engine</h4>
              <p className="text-[10px] text-blue-400 font-bold tracking-widest uppercase">v3.5 Professional</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-gray-800/50">
              <span className="text-[10px] font-bold text-gray-500 uppercase">Status</span>
              <Badge variant="success" className="animate-pulse">Active</Badge>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-800/50">
              <span className="text-[10px] font-bold text-gray-500 uppercase">Intelligence Track</span>
              <span className="text-[10px] font-black text-white uppercase">Dual-Track AI</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-800/50">
              <span className="text-[10px] font-bold text-gray-500 uppercase">Extraction Fidelity</span>
              <span className="text-[10px] font-black text-white uppercase">98.2%</span>
            </div>
          </div>
        </Card>
      </section>

      <section className="space-y-4">
        <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Corpus Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <Card className="!p-4 bg-gray-900/40 text-center">
            <div className="text-2xl font-black text-white">{stats.totalPapers}</div>
            <div className="text-[8px] font-black text-gray-500 uppercase mt-1">Documents</div>
          </Card>
          <Card className="!p-4 bg-gray-900/40 text-center">
            <div className="text-2xl font-black text-white">{stats.domains}</div>
            <div className="text-[8px] font-black text-gray-500 uppercase mt-1">Domains</div>
          </Card>
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Quick Tips</h3>
        <div className="space-y-3">
          {[
            { t: "Deep Gap Detection", d: "Upload multiple papers in the same field to see emerging gaps." },
            { t: "Evidence Grounding", d: "Click on any paper to see exact quotes backing every AI insight." },
            { t: "Trend Analysis", d: "Use the Comparison Matrix to track methodology shifts over time." }
          ].map((item, i) => (
            <div key={i} className="p-4 bg-gray-900/20 border border-gray-800/50 rounded-2xl group hover:bg-gray-800/30 transition-colors">
              <h5 className="text-[10px] font-black text-white uppercase mb-1 group-hover:text-blue-400 transition-colors">{item.t}</h5>
              <p className="text-[10px] text-gray-500 leading-relaxed font-medium">{item.d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
