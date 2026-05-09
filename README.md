# ResearchGap AI 🔬
### Professional AI-Powered Academic Research Analyst Dashboard

ResearchGap AI is a high-fidelity intelligence layer designed to unpack academic papers, identify genuine contributions, and detect unresolved research gaps with deterministic evidence grounding.

---

## 🚀 Key Features

- **Evidence-Grounded Intelligence:** Every AI-generated insight is linked to an exact quote from the source PDF, preventing hallucinations.
- **Dual-Track Reasoning:** Combines Large Language Models (LLM) with a robust heuristic NLP engine for zero-failure reliability.
- **Semantic Section Mapping:** Automatically partitions documents into core academic sections (Abstract, Methodology, Experiments, etc.).
- **Cross-Paper Comparison:** Side-by-side methodological and performance matrix for rapid corpus auditing.
- **Reliability Scoring:** Mathematically derived scores for reproducibility, rigor, and technical complexity.
- **Privacy-First Design:** Transient session handling with aggressive data purging upon session termination.

---

## 🛠️ Architecture

### 🧠 Backend (FastAPI + Python)
- **Extraction:** PyMuPDF & PDFPlumber hybrid pipeline.
- **Processing:** Section-aware semantic chunking.
- **AI Layer:** Google Gemini Flash v2 (Consolidated 1-call architecture).
- **Hardening:** High-fidelity regex-based academic pattern matching fallback.
- **Database:** PostgreSQL with JSONB for flexible intelligence report storage.

### 🎨 Frontend (React + Vite)
- **Stack:** React 19, Tailwind CSS 4.
- **UX:** Workspace-split dashboard (65% Work / 35% Intel).
- **Visuals:** Dynamic confidence indicators, evidence cards, and modal-based deep dives.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Gemini API Key

### Backend Setup
1. `cd backend`
2. `pip install -r requirements.txt`
3. Create `.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   DATABASE_URL=postgresql://user:pass@localhost:5432/db
   ```
4. `uvicorn main:app --reload`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---

## 📦 Deployment

- **Frontend:** Optimized for **Vercel** (`npm run build`).
- **Backend:** Ready for **Render** or **Railway**.
- **Database:** Managed **Supabase** or **AWS RDS**.

---

## 📈 Future Scope
- **ArXiv Live Feed:** Real-time monitoring of new publications.
- **Collaborative Workspaces:** Multi-user shared corpus analysis.
- **Automated Lit-Review:** One-click generation of comprehensive literature review drafts.

---

## 📄 License
MIT License. Professional Academic Project.

---

### Developed for Portfolio & Research Excellence.
