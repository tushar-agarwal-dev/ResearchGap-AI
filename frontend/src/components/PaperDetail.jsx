import { Badge } from './ui/Badge';
import { Card } from './ui/Card';
import { Button } from './ui/Button';

const ConfidenceBar = ({ value }) => (
  <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden mt-1">
    <div 
      className={`h-full transition-all duration-1000 ${value > 0.8 ? 'bg-emerald-500' : value > 0.5 ? 'bg-yellow-500' : 'bg-red-500'}`}
      style={{ width: `${(value || 0) * 100}%` }}
    />
  </div>
);

const EvidenceCard = ({ item, titleLabel = "Insight" }) => {
  if (!item || !item.text) return null;
  return (
    <Card className="!p-5 bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition-colors">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-sm font-bold text-white pr-4">{item.text}</h4>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <Badge variant="indigo" className="!text-[9px] uppercase tracking-wider">{item.source_section || 'Unknown'}</Badge>
          <span className="text-[10px] text-gray-500 font-bold">Conf: {((item.confidence || 0) * 100).toFixed(0)}%</span>
        </div>
      </div>
      
      {item.reasoning && (
        <p className="text-xs text-gray-300 font-medium mb-4 leading-relaxed border-l-2 border-blue-500/50 pl-3">
          {item.reasoning}
        </p>
      )}

      {item.evidence && (
        <div className="mt-4 p-3 bg-black/50 rounded-lg border border-gray-800/50 relative">
          <div className="absolute -top-2 left-3 bg-gray-900 px-2 text-[9px] font-black text-gray-500 uppercase tracking-widest">Grounded Evidence</div>
          <p className="text-[11px] text-gray-400 italic leading-relaxed pt-1">"{item.evidence}"</p>
        </div>
      )}
    </Card>
  );
};

export const PaperDetail = ({ paper, onRunAnalysis, isAnalyzing }) => {
  const { insights, intelligence_report: report } = paper;

  if (!report || !report.contributions) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center space-y-6">
        <div className={`w-16 h-16 bg-blue-600/10 rounded-full flex items-center justify-center text-blue-500 ${isAnalyzing ? 'animate-pulse' : ''}`}>
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m12 14 4-4"/><path d="m3.34 19 8.66-16.6a.5.5 0 0 1 .9 0L21.56 19a.5.5 0 0 1-.4.8H3.74a.5.5 0 0 1-.4-.8z"/><path d="M12 10V6"/></svg>
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-black text-white">Intelligence Report Missing</h3>
          <p className="text-sm text-gray-500 max-w-sm">This paper requires AI-powered reasoning pipeline extraction.</p>
        </div>
        <Button 
          variant="primary" 
          className="!px-8 !py-3" 
          onClick={() => onRunAnalysis(paper.id)}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2" />
              Running LLM Pipeline...
            </>
          ) : (
            'Run Intelligence Engine'
          )}
        </Button>
      </div>
    );
  }

  const { 
    executive_summary: exec = {}, 
    contributions = [], 
    research_gaps: gaps = [], 
    strengths = [], 
    limitations = [], 
    future_directions: future = [], 
    recommendation: rec = {}, 
    reliability = {} 
  } = report;

  return (
    <div className="space-y-12 pb-20 animate-fade-in">
      {/* 1. Executive Summary & Readiness */}
      <section className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          <div className="flex flex-wrap gap-2">
            <Badge variant="primary">{exec?.domain_category || insights?.domain || 'General Research'}</Badge>
            <Badge variant="indigo">{insights?.complexity || 'Intermediate'}</Badge>
            <Badge variant="purple">{insights?.reading_time || 10} min read</Badge>
          </div>
          <div className="space-y-4">
             <h3 className="text-sm font-black text-white uppercase tracking-widest">Problem Statement</h3>
             <p className="text-gray-300 leading-relaxed text-lg font-medium">{exec?.problem_statement || "No specific problem statement extracted."}</p>
             <h3 className="text-sm font-black text-gray-500 uppercase tracking-widest">Primary Objective</h3>
             <p className="text-gray-400 text-sm leading-relaxed bg-gray-800/20 p-4 rounded-2xl border border-gray-800/50">{exec?.primary_objective || "Core objective details unavailable."}</p>
          </div>
        </div>
        
        <div className="space-y-6">
           <Card className="!p-6 text-center bg-gradient-to-br from-blue-600/20 to-indigo-600/10 border-blue-500/20">
              <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-2">Should I Read This?</h4>
              <div className="text-5xl font-black text-white mb-2">{rec?.read_score || 50}<span className="text-sm opacity-40">/100</span></div>
              <p className="text-[11px] text-gray-300 font-bold leading-tight px-4 pb-4">{rec?.explanation || "Assessment based on overall methodological rigor."}</p>
              {rec?.should_read_this && (
                 <Badge variant="success" className="mx-auto mt-2">Highly Recommended</Badge>
              )}
           </Card>

           <Card className="!p-4 bg-gray-900/40">
              <div className="flex justify-between items-center mb-3">
                <h4 className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Reliability Score</h4>
                <span className="text-lg font-black text-white">{((reliability?.score || 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="space-y-3">
                {Object.entries(reliability?.signals || {}).map(([key, val]) => (
                  <div key={key} className="flex justify-between items-center text-[10px] font-bold text-gray-500 uppercase">
                    <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                    <Badge variant={val ? "success" : "neutral"} className="!px-1.5 !py-0">{val ? "Yes" : "No"}</Badge>
                  </div>
                ))}
              </div>
           </Card>
        </div>
      </section>

      {/* 2. Contributions */}
      {contributions.length > 0 && (
      <section className="space-y-6">
         <div className="flex items-center gap-4">
           <h2 className="text-2xl font-black text-white uppercase tracking-tight">Genuine Contributions</h2>
           <div className="h-px flex-1 bg-gray-800" />
         </div>
         <div className="grid md:grid-cols-2 gap-4">
            {contributions.map((c, i) => <EvidenceCard key={i} item={c} />)}
         </div>
      </section>
      )}

      {/* 3. Research Gaps & Limitations */}
      <section className="grid md:grid-cols-2 gap-8">
         {gaps.length > 0 && (
         <div className="space-y-6">
            <h2 className="text-lg font-black text-rose-400 uppercase tracking-widest">Unresolved Gaps</h2>
            <div className="space-y-4">
               {gaps.map((g, i) => <EvidenceCard key={`gap-${i}`} item={g} />)}
            </div>
         </div>
         )}
         
         {limitations.length > 0 && (
         <div className="space-y-6">
            <h2 className="text-lg font-black text-yellow-500 uppercase tracking-widest">Critical Limitations</h2>
            <div className="space-y-4">
               {limitations.map((l, i) => <EvidenceCard key={`lim-${i}`} item={l} />)}
            </div>
         </div>
         )}
      </section>

      {/* 4. Strengths & Future Work */}
      <section className="grid md:grid-cols-2 gap-8 pt-8 border-t border-gray-800">
         {strengths.length > 0 && (
         <div className="space-y-6">
            <h2 className="text-lg font-black text-emerald-400 uppercase tracking-widest">Validated Strengths</h2>
            <div className="space-y-4">
               {strengths.map((s, i) => <EvidenceCard key={`str-${i}`} item={s} />)}
            </div>
         </div>
         )}
         
         {future.length > 0 && (
         <div className="space-y-6">
            <h2 className="text-lg font-black text-blue-400 uppercase tracking-widest">Future Directions</h2>
            <div className="space-y-4">
               {future.map((f, i) => <EvidenceCard key={`fut-${i}`} item={f} />)}
            </div>
         </div>
         )}
      </section>
    </div>
  );
};
