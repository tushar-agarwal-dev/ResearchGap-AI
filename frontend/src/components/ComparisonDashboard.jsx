import { Badge } from './ui/Badge';

export const ComparisonDashboard = ({ papers }) => {
  if (!papers || papers.length === 0) return null;

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tight">Cross-Paper Comparison</h2>
          <p className="text-xs text-gray-500 font-bold uppercase tracking-widest mt-1">Methodological Performance Matrix</p>
        </div>
        <Badge variant="purple">{papers.length} Papers compared</Badge>
      </header>

      <div className="overflow-x-auto rounded-2xl border border-gray-800 bg-gray-900/30 backdrop-blur-md">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-800/50">
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-800">Research Paper</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-800">Methodology</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-800">Dataset</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-800">Performance</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-800 text-center">Reproducibility</th>
            </tr>
          </thead>
          <tbody>
            {papers.map((paper) => (
              <tr key={paper.id} className="hover:bg-blue-500/5 transition-colors group">
                <td className="p-4 border-b border-gray-800">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-gray-200 group-hover:text-blue-400 transition-colors">{paper.filename}</span>
                    <span className="text-[10px] text-gray-500 font-mono mt-0.5">{paper.insights?.domain}</span>
                  </div>
                </td>
                <td className="p-4 border-b border-gray-800">
                  <div className="flex flex-wrap gap-1">
                    {(paper.insights?.algorithms || []).slice(0, 2).map(a => (
                      <Badge key={a} variant="default" className="!bg-gray-800/50 !text-[8px]">{a}</Badge>
                    ))}
                    {(paper.insights?.algorithms || []).length > 2 && <span className="text-[8px] text-gray-600 font-bold">+{paper.insights.algorithms.length - 2} more</span>}
                  </div>
                </td>
                <td className="p-4 border-b border-gray-800">
                  <span className="text-xs text-gray-300 font-medium">{(paper.insights?.datasets || []).join(', ') || 'Custom'}</span>
                </td>
                <td className="p-4 border-b border-gray-800">
                  <span className="text-sm font-black text-emerald-400">{paper.insights?.results?.metrics?.accuracy || 'N/A'}</span>
                </td>
                <td className="p-4 border-b border-gray-800">
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden max-w-[80px]">
                      <div 
                        className="h-full bg-blue-500 rounded-full" 
                        style={{ width: `${(paper.insights?.reproducibility_score || 0.6) * 100}%` }}
                      />
                    </div>
                    <span className="text-[9px] font-bold text-gray-500">{(paper.insights?.reproducibility_score || 0.6).toFixed(2)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
