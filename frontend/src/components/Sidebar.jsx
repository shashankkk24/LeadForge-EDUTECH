import React from 'react';

const NAV_TABS = [
  { id: 'dashboard',    icon: 'dashboard',        label: 'Dashboard'    },
  { id: 'scraper',      icon: 'search_insights',  label: 'Lead Scraper' },
  { id: 'intelligence', icon: 'psychology',        label: 'Intelligence' },
  { id: 'outreach',     icon: 'forward_to_inbox', label: 'Outreach'     },
  { id: 'analytics',   icon: 'bar_chart',         label: 'Analytics'    },
];

export default function Sidebar({ activeTab, setActiveTab, onNewPipeline, pipelines = [], isConnected }) {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-[#0f172a] flex flex-col z-40 select-none">

      {/* ── Logo ── */}
      <div className="flex items-center gap-3 px-5 pt-6 pb-5">
        <div className="w-9 h-9 rounded-xl bg-blue-500 flex items-center justify-center shadow-lg shadow-blue-500/40 shrink-0">
          <span className="material-symbols-outlined text-white text-[20px]" style={{fontVariationSettings:"'FILL' 1"}}>psychology</span>
        </div>
        <div>
          <p className="text-white font-black text-[15px] leading-tight" style={{fontFamily:'Manrope,sans-serif'}}>LeadForge EDU</p>
          <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">AI Sales Engine</p>
        </div>
      </div>

      {/* ── New Pipeline ── */}
      <div className="px-4 mb-4">
        <button
          onClick={onNewPipeline}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold transition-colors shadow-md shadow-blue-600/30"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Pipeline
        </button>
      </div>

      {/* ── Nav ── */}
      <nav className="flex-1 flex flex-col gap-0.5 px-3 overflow-y-auto scrollbar-hide">
        {NAV_TABS.map(tab => {
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold w-full text-left transition-all ${
                active
                  ? 'bg-blue-600/20 text-blue-400'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              <span
                className="material-symbols-outlined text-[20px]"
                style={active ? {fontVariationSettings:"'FILL' 1"} : {}}
              >
                {tab.icon}
              </span>
              {tab.label}
              {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-400" />}
            </button>
          );
        })}
      </nav>

      {/* ── Pipelines ── */}
      {pipelines.length > 0 && (
        <div className="px-4 mt-2 mb-3">
          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600 mb-2 px-1">My Pipelines</p>
          <div className="flex flex-col gap-1">
            {pipelines.map(p => (
              <div key={p.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 text-xs font-semibold text-slate-400">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                {p.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Footer ── */}
      <div className="px-4 pb-5 pt-3 border-t border-white/5">
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold ${
          isConnected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-white/5 text-slate-500'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
          {isConnected ? 'WebSocket Live' : 'Connecting…'}
        </div>
      </div>
    </aside>
  );
}
