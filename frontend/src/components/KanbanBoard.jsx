import React from 'react';
import LeadCard from './LeadCard';

const COLUMNS = [
  { status: 'New',       label: 'New',       dot: 'bg-indigo-500',  count: 'bg-indigo-50 text-indigo-600',  icon: 'fiber_new'       },
  { status: 'Drafted',   label: 'Drafted',   dot: 'bg-purple-500',  count: 'bg-purple-50 text-purple-600',  icon: 'edit_note'       },
  { status: 'Contacted', label: 'Contacted', dot: 'bg-emerald-500', count: 'bg-emerald-50 text-emerald-600',icon: 'mark_email_read' },
  { status: 'Closed',    label: 'Closed',    dot: 'bg-slate-400',   count: 'bg-slate-100 text-slate-500',   icon: 'check_circle'    },
];

/* Sort: HOT → WARM → COLD, then score desc */
function sortLeads(leads) {
  const order = { HOT: 0, WARM: 1, COLD: 2 };
  return [...leads].sort((a, b) => {
    const pa = order[a.priority] ?? 2;
    const pb = order[b.priority] ?? 2;
    if (pa !== pb) return pa - pb;
    return (b.lead_score || 0) - (a.lead_score || 0);
  });
}

export default function KanbanBoard({ leads, onLeadClick, loading }) {
  const sorted = sortLeads(leads);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3 text-slate-400">
          <div className="w-10 h-10 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
          <p className="text-sm font-medium">Loading pipeline…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-x-auto bg-slate-50 h-full min-h-0">
      <div className="flex gap-5 h-full p-6 min-w-max">
        {COLUMNS.map(col => {
          const colLeads = sorted.filter(l => l.status === col.status);
          return (
            <div key={col.status} className="w-[280px] flex flex-col gap-3 h-full">

              {/* Column header */}
              <div className="flex items-center gap-2 px-1 shrink-0">
                <div className={`w-2 h-2 rounded-full ${col.dot}`} />
                <span className="font-bold text-sm text-slate-700" style={{fontFamily:'Manrope,sans-serif'}}>
                  {col.label}
                </span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${col.count}`}>
                  {colLeads.length}
                </span>
              </div>

              {/* Cards */}
              <div className="flex flex-col gap-3 overflow-y-auto pb-8 flex-1 scrollbar-hide kanban-col">
                {colLeads.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-14 border-2 border-dashed border-slate-200 rounded-xl text-slate-300">
                    <span className="material-symbols-outlined text-3xl mb-2">{col.icon}</span>
                    <p className="text-xs font-medium">No {col.label.toLowerCase()} leads</p>
                  </div>
                ) : (
                  colLeads.map(lead => (
                    <LeadCard key={lead.id} lead={lead} onClick={onLeadClick} />
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
