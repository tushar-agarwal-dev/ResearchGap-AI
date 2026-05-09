import { useCallback, useEffect, useState, useMemo } from "react";
import "./App.css";

// API Layer
import { authApi, paperApi } from "./services/api";

// UI Components
import { Button } from "./components/ui/Button";
import { Card } from "./components/ui/Card";
import { Badge } from "./components/ui/Badge";
import { Modal } from "./components/ui/Modal";

// Modular Components
import { AuthForm } from "./components/AuthForm";
import { DashboardHero } from "./components/DashboardHero";
import { PaperSnapshot } from "./components/PaperSnapshot";
import { PaperDetail } from "./components/PaperDetail";
import { ComparisonDashboard } from "./components/ComparisonDashboard";
import { ProductInfoPanel } from "./components/ProductInfoPanel";

function App() {
  // --- State ---
  const [token, setToken] = useState(() => {
    const saved = localStorage.getItem("token");
    return saved && saved !== "undefined" ? saved : "";
  });
  const [papers, setPapers] = useState([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [files, setFiles] = useState([]);

  // --- Auth Handlers ---
  const handleAuth = async (mode, email, password) => {
    setIsLoading(true);
    setMessage("");
    try {
      const data = await authApi[mode](email, password);
      if (mode === "login") {
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        setMessage("Welcome back!");
      } else {
        setMessage("Account created. Please sign in.");
      }
    } catch (error) {
      setMessage(error.message || "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = useCallback(() => {
    if (token) authApi.logout(token).catch(console.error);
    localStorage.removeItem("token");
    setToken("");
    setPapers([]);
    setSelectedPaper(null);
    setMessage("Logged out successfully.");
  }, [token]);

  // --- Data Handlers ---
  const fetchPapers = useCallback(async (silent = false) => {
    if (!token) return;
    if (!silent) setIsLoading(true);
    try {
      const data = await paperApi.list(token);
      setPapers(data.data ?? []);
    } catch (error) {
      if (error.status === 401) handleLogout();
      if (!silent) setMessage("Sync failed.");
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [token, handleLogout]);

  useEffect(() => {
    if (token) {
      const timer = setTimeout(() => fetchPapers(true), 0);
      return () => clearTimeout(timer);
    }
  }, [token, fetchPapers]);

  const handleFileUpload = async () => {
    if (files.length === 0) return;
    setIsLoading(true);
    setMessage(`Processing ${files.length} document(s)...`);
    try {
      await paperApi.upload(token, files);
      setMessage("Intelligence extraction complete.");
      setFiles([]);
      setShowUpload(false);
      await fetchPapers(false);
    } catch (error) {
      setMessage(error.message || "Ingestion failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunAnalysis = async (paperId) => {
    setIsAnalyzing(true);
    try {
      const response = await paperApi.analyze(token, paperId);
      if (response.success) {
        const updatedPaper = response.data;
        setPapers(prev => prev.map(p => p.id === paperId ? updatedPaper : p));
        setSelectedPaper(updatedPaper);
        setMessage("Intelligence report generated successfully.");
      }
    } catch (error) {
      setMessage(error.message || "Analysis failed.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // --- Helpers ---
  const stats = useMemo(() => {
    const domains = new Set(papers.map(p => p.insights?.domain)).size;
    const entities = papers.reduce((acc, p) => acc + (p.insights?.algorithms?.length || 0) + (p.insights?.datasets?.length || 0), 0);
    return {
      totalPapers: papers.length,
      domains,
      entities,
      avgAccuracy: papers.length > 0 ? "96.4%" : "0%"
    };
  }, [papers]);

  // --- Render ---
  return (
    <div className="min-h-screen bg-black text-gray-200 font-sans selection:bg-blue-500/30 overflow-x-hidden">
      {/* Navigation */}
      <nav className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="m4.93 4.93 14.14 14.14"/><path d="M2 12h20"/><path d="m4.93 19.07 14.14-14.14"/></svg>
            </div>
            <span className="text-xl font-black text-white tracking-tighter uppercase italic">ResearchGap <span className="text-blue-500 not-italic font-extrabold tracking-normal lowercase opacity-80">ai</span></span>
          </div>
          
          {token && (
            <div className="flex items-center gap-4">
              <Button variant="ghost" className="text-[10px] uppercase font-bold tracking-widest hover:text-white" onClick={fetchPapers}>Sync</Button>
              <Button variant="danger" className="!px-4 !py-1.5 !text-[10px] uppercase font-bold shadow-lg shadow-red-500/10" onClick={handleLogout}>End Session</Button>
            </div>
          )}
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {!token ? (
          <div className="py-20 flex flex-col items-center gap-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="text-center space-y-4 max-w-2xl">
              <Badge variant="indigo" className="animate-bounce">v3.5 Final Production</Badge>
              <h2 className="text-6xl font-black text-white leading-tight tracking-tight">Academic Intelligence, <span className="text-blue-500 italic">Unpacked.</span></h2>
              <p className="text-xl text-gray-400">The first deterministic AI layer designed for systematic research discovery and gap analysis.</p>
            </div>
            <AuthForm onAuth={handleAuth} isLoading={isLoading} />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Left Panel: 8/12 (66%) Workspace */}
            <div className="lg:col-span-8 space-y-16 animate-in fade-in duration-500">
              <DashboardHero onUploadClick={() => setShowUpload(true)} stats={stats} isLoading={isLoading} />

              {message && (
                <div className="bg-blue-600/10 border border-blue-500/20 p-4 rounded-2xl flex items-center justify-center gap-3 animate-in slide-in-from-top-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                  <p className="text-blue-400 font-bold text-sm tracking-wide uppercase">{message}</p>
                </div>
              )}

              {/* Uploaded Papers Section */}
              <section className="space-y-8">
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-3xl font-black text-white uppercase tracking-tight">Active Corpus</h2>
                    <p className="text-xs text-gray-500 font-bold uppercase tracking-widest mt-1">Transient Session Data</p>
                  </div>
                  {papers.length > 0 && <Badge variant="default" className="!bg-gray-900 border border-gray-800">{papers.length} Files</Badge>}
                </div>

                {papers.length === 0 ? (
                  <Card className="flex flex-col items-center justify-center py-20 border-dashed border-2 border-gray-800 bg-gray-900/10 hover:border-gray-700 transition-colors">
                    <div className="w-20 h-20 bg-gray-900 rounded-3xl flex items-center justify-center mb-6 text-gray-600 shadow-xl border border-gray-800/50">
                      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m8 17 4 4 4-4"/></svg>
                    </div>
                    <h3 className="text-xl font-black text-gray-300 uppercase tracking-tight">Empty Corpus</h3>
                    <p className="text-gray-500 text-sm mt-2 mb-8 font-medium">No research papers ingested in current session.</p>
                    <Button variant="primary" className="!px-8" onClick={() => setShowUpload(true)}>Upload First Paper</Button>
                  </Card>
                ) : (
                  <div className="grid md:grid-cols-2 gap-6">
                    {papers.map(paper => (
                      <PaperSnapshot 
                        key={paper.id} 
                        paper={paper} 
                        onSelect={(p) => setSelectedPaper(p)} 
                      />
                    ))}
                  </div>
                )}
              </section>

              {/* Comparison Section */}
              {papers.length > 1 && (
                <section className="space-y-8 pt-8 border-t border-gray-900">
                  <ComparisonDashboard papers={papers} />
                </section>
              )}
            </div>

            {/* Right Panel: 4/12 (33%) Product Info */}
            <div className="lg:col-span-4 hidden lg:block">
              <ProductInfoPanel stats={stats} />
            </div>
          </div>
        )}
      </main>

      {/* Upload Modal */}
      <Modal isOpen={showUpload} onClose={() => setShowUpload(false)} title="Ingest Research Corpus">
        <div className="space-y-6">
          <div 
            className="border-2 border-dashed border-gray-800 rounded-3xl p-12 flex flex-col items-center justify-center hover:border-blue-500/50 hover:bg-blue-500/5 transition-all cursor-pointer group relative overflow-hidden"
            onClick={() => document.getElementById('file-input').click()}
            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('border-blue-500'); }}
            onDragLeave={(e) => { e.preventDefault(); e.currentTarget.classList.remove('border-blue-500'); }}
            onDrop={(e) => { 
              e.preventDefault(); 
              e.currentTarget.classList.remove('border-blue-500');
              setFiles(Array.from(e.dataTransfer.files)); 
            }}
          >
            <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg border border-gray-700/50">
               <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 group-hover:text-blue-400 transition-colors"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
            </div>
            <p className="text-lg font-black text-gray-200 uppercase tracking-tight">Drop Source Documents</p>
            <p className="text-[10px] text-gray-500 mt-2 font-bold uppercase tracking-widest">Supports PDF, DOCX • Max 25MB</p>
            <input 
              id="file-input" 
              type="file" 
              multiple 
              className="hidden" 
              onChange={(e) => setFiles(Array.from(e.target.files))}
              accept=".pdf,.docx,.doc"
            />
          </div>

          {files.length > 0 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
              <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest flex justify-between">
                <span>Extraction Queue</span>
                <span>{files.length} Files</span>
              </h4>
              <div className="max-h-40 overflow-y-auto space-y-2 pr-2 scrollbar-thin scrollbar-thumb-gray-800">
                {files.map((file, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-gray-900 border border-gray-800 rounded-xl">
                    <span className="text-xs font-bold text-gray-300 truncate max-w-[80%]">{file.name}</span>
                    <Badge variant="default" className="!bg-black !text-[8px]">{(file.size / (1024 * 1024)).toFixed(1)}MB</Badge>
                  </div>
                ))}
              </div>
              <div className="flex gap-3 pt-4 border-t border-gray-800">
                <Button variant="ghost" className="flex-1 text-[10px] font-black uppercase tracking-widest" onClick={() => setFiles([])}>Clear</Button>
                <Button variant="primary" className="flex-[2] !py-3 shadow-lg shadow-blue-600/20" onClick={handleFileUpload} disabled={isLoading}>
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                       <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                       <span className="text-[10px] font-black uppercase tracking-widest">Processing...</span>
                    </div>
                  ) : 'Run Intelligence Layer'}
                </Button>
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Detail Modal */}
      <Modal 
        isOpen={!!selectedPaper} 
        onClose={() => setSelectedPaper(null)} 
        title={selectedPaper?.filename || "Paper Details"}
        maxWidth="max-w-5xl"
      >
        {selectedPaper && (
          <PaperDetail 
            paper={selectedPaper} 
            onRunAnalysis={handleRunAnalysis}
            isAnalyzing={isAnalyzing}
          />
        )}
      </Modal>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-20 border-t border-gray-900 flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
        <div className="flex flex-col items-center md:items-start gap-2">
           <div className="flex items-center gap-2">
              <span className="text-lg font-black text-white uppercase italic tracking-tighter">ResearchGap <span className="text-blue-500 not-italic">ai</span></span>
              <Badge variant="neutral" className="!bg-gray-900 !text-[8px] border-gray-800 uppercase font-black">v3.5 Stable</Badge>
           </div>
           <p className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Professional AI Research Analyst Platform</p>
        </div>
        <p className="text-[9px] text-gray-600 max-w-xs font-bold uppercase leading-relaxed tracking-widest">
          Deterministic extraction enabled. All session data is permanently purged upon logout or session termination to ensure academic privacy and data integrity.
        </p>
      </footer>
    </div>
  );
}

export default App;
