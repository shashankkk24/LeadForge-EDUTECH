import React from 'react';

/* ── Priority config ─────────────────────────────────────────────────────── */
const PRIORITY = {
  HOT:  { badge: 'bg-red-100 text-red-600 border-red-200',    bar: 'bg-red-500',    dot: 'bg-red-500'    },
  WARM: { badge: 'bg-orange-100 text-orange-600 border-orange-200', bar: 'bg-orange-400', dot: 'bg-orange-400' },
  COLD: { badge: 'bg-blue-100 text-blue-600 border-blue-200', bar: 'bg-blue-400',   dot: 'bg-blue-400'   },
};

/* ── Intent config ───────────────────────────────────────────────────────── */
const INTENT = {
  ACTIVELY_SEEKING:        { label: 'Actively Seeking',    cls: 'bg-red-50 text-red-700'     },
  FRUSTRATED_CURRENT_USER: { label: 'Frustrated User',     cls: 'bg-orange-50 text-orange-700' },
  BUDGET_APPROVED:         { label: 'Budget Approved',     cls: 'bg-green-50 text-green-700'  },
  PEER_RECOMMENDATION_ASK: { label: 'Peer Rec Ask',        cls: 'bg-purple-50 text-purple-700' },
  RESEARCH_PHASE:          { label: 'Research Phase',      cls: 'bg-slate-100 text-slate-600'  },
};

/* ── Reddit SVG icon ─────────────────────────────────────────────────────── */
const RedditIcon = () => (
  <svg viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 text-orange-600">
    <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm5.93 10.01c.03.2.05.4.05.6 0 3.07-3.58 5.56-8 5.56s-8-2.49-8-5.56c0-.2.02-.4.05-.6a1.5 1.5 0 10-1.55-2.5 1.5 1.5 0 001.5 1.5c.13 0 .26-.02.38-.05C1.1 10.5 1 11.24 1 12c0 3.87 4.03 7 9 7s9-3.13 9-7c0-.76-.1-1.5-.33-2.14.12.03.25.05.38.05a1.5 1.5 0 001.5-1.5 1.5 1.5 0 00-1.5-1.5 1.5 1.5 0 00-1.55 2.5zM7 11a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm6 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm-5.5 2.5c.28.28.65.5 1 .65.35.14.73.22 1.5.22s1.15-.08 1.5-.22c.35-.15.72-.37 1-.65.2-.2.5-.2.7 0 .2.2.2.5 0 .7-.4.4-.9.7-1.4.88-.5.18-1.1.27-1.8.27s-1.3-.09-1.8-.27c-.5-.18-1-.48-1.4-.88-.2-.2-.2-.5 0-.7.2-.2.5-.2.7 0z"/>
  </svg>
);

export default function LeadCard({ lead, onClick }) {
  const priority = lead.priority || 'COLD';
  const p = PRIORITY[priority] || PRIORITY.COLD;
  const score = lead.lead_score || 0;
  const intentCfg = INTENT[lead.intent_label] || { label: lead.intent_label || '', cls: 'bg-slate-100 text-slate-500' };
  const tags = Array.isArray(lead.pain_point_tags) ? lead.pain_point_tags : [];

  const timeAgo = (() => {
    const d = lead.extracted_at || lead.created_at;
    if (!d) return 'Just now';
    const diff = Date.now() - new Date(d).getTime();
    const h = Math.floor(diff / 3600000);
    if (h < 1) return 'Just now';
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  })();

  return (
    <div
      onClick={() => onClick(lead)}
      className="bg-white rounded-xl border border-slate-200 p-4 cursor-pointer hover:shadow-md hover:border-blue-300 hover:-translate-y-0.5 transition-all group"
    >
      {/* ── Row 1: platform + priority ── */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-1.5">
          <div className="w-5 h-5 rounded bg-orange-100 flex items-center justify-center">
            <RedditIcon />
          </div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            {lead.platform || 'reddit'}
          </span>
        </div>
        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full border ${p.badge}`}>
          {priority}
        </span>
      </div>

      {/* ── Username ── */}
      <p className="font-bold text-sm text-slate-900 mb-1 truncate">
        u/{lead.username || 'unknown'}
      </p>

      {/* ── Post content ── */}
      <p className="text-xs text-slate-500 line-clamp-2 mb-3 leading-relaxed min-h-[32px]">
        {lead.post_content || 'No content available.'}
      </p>

      {/* ── Intent label ── */}
      {lead.intent_label && (
        <div className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold mb-2.5 ${intentCfg.cls}`}>
          {intentCfg.label}
        </div>
      )}

      {/* ── Pain point tags ── */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {tags.slice(0, 3).map(tag => (
            <span key={tag} className="bg-slate-100 text-slate-600 text-[10px] font-semibold px-2 py-0.5 rounded-full">
              #{tag.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      )}

      {/* ── HeatScore bar ── */}
      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">HeatScore</span>
          <span className="text-[11px] font-black text-slate-700">{score}/100</span>
        </div>
        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${p.bar}`} style={{ width: `${score}%` }} />
        </div>
      </div>

      {/* ── Footer: role · urgency · time ── */}
      <div className="flex items-center justify-between pt-2.5 border-t border-slate-100">
        <div className="flex items-center gap-1 min-w-0">
          {lead.detected_role && (
            <span className="text-[10px] text-slate-400 font-medium capitalize truncate">
              {lead.detected_role}
            </span>
          )}
          {lead.urgency_level && (
            <span className={`text-[10px] font-bold ml-1 shrink-0 ${
              lead.urgency_level === 'high'   ? 'text-red-500' :
              lead.urgency_level === 'medium' ? 'text-orange-500' : 'text-slate-400'
            }`}>
              · {lead.urgency_level}
            </span>
          )}
        </div>
        <span className="text-[10px] text-slate-400 shrink-0 ml-2">{timeAgo}</span>
      </div>
    </div>
  );
}
