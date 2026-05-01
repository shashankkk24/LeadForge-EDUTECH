import React, { useEffect, useState } from 'react';
import { getLeadIntelligence } from '../services/api';

const PRIORITY_BADGE = {
  HOT:  'bg-red-100 text-red-600',
  WARM: 'bg-orange-100 text-orange-600',
  COLD: 'bg-blue-100 text-blue-600',
};

export default function IntelCard({ lead, onClose, onGenerateMessage }) {
  const [intel, setIntel]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  useEffect(() => {
    if (!lead) return;
    setIntel(null);
    setError(null);
    setLoading(true);
    getLeadIntelligence(lead.id)
      .then(setIntel)
      .catch(() => setError('Could not load intelligence data.'))
      .finally(() => setLoading(false));
  }, [lead?.id]);

  if (!lead) return null;

  const tags = Array.isArray(lead.pain_point_tags) ? lead.pain_point_tags : [];

  return (
    <div className="fixed bottom-6 right-6 w-[380px] bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col z-50"
         style={{maxHeight: 'calc(100vh - 80px)', top: '70px', bottom: 'auto'}}>

      {/* ── Header ── */}
      <div className="bg-gradient-to-r from-[#1e3a8a] to-[#4f46e5] px-5 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-white text-[20px]" style={{fontVariationSettings:"'FILL' 1"}}>auto_awesome</span>
          <span className="text-white font-bold text-sm">Lead Intelligence</span>
        </div>
        <button onClick={onClose} className="text-blue-200 hover:text-white p-1 rounded-lg hover:bg-white/10">
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>

      {/* ── Body ── */}
      <div className="flex flex-col gap-4 p-5 overflow-y-auto flex-1 scrollbar-hide">

        {/* Lead summary row */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-slate-100 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-slate-400 text-2xl" style={{fontVariationSettings:"'FILL' 1"}}>account_circle</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-sm text-slate-900 truncate">u/{lead.username}</p>
            <p className="text-xs text-slate-500 capitalize">{lead.detected_role || 'Unknown role'}</p>
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${PRIORITY_BADGE[lead.priority] || 'bg-slate-100 text-slate-500'}`}>
              {lead.priority}
            </span>
            <span className="text-xs font-black text-slate-700">{lead.lead_score}/100</span>
          </div>
        </div>

        {/* Reddit post link */}
        {lead.post_url && (
          <a
            href={lead.post_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-800 font-semibold"
          >
            <span className="material-symbols-outlined text-[14px]">open_in_new</span>
            View original Reddit post
          </a>
        )}

        {/* Pain point tags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {tags.map(tag => (
              <span key={tag} className="bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-1 rounded-full border border-blue-100">
                #{tag.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        )}

        {/* Intelligence sections */}
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-8 h-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
          </div>
        ) : error ? (
          <p className="text-center text-slate-400 text-sm py-4">{error}</p>
        ) : intel ? (
          <div className="flex flex-col gap-3">

            {/* Opening line */}
            {intel.talk_track && (
              <div className="p-3 bg-blue-50 rounded-xl border border-blue-100">
                <p className="text-[10px] font-bold text-blue-500 uppercase tracking-wider mb-1.5">Opening Line</p>
                <p className="text-sm text-blue-900 font-medium leading-relaxed">{intel.talk_track}</p>
              </div>
            )}

            {/* Feature highlights */}
            {intel.feature_highlights?.length > 0 && (
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider mb-2">Key Features to Highlight</p>
                <ul className="flex flex-col gap-1.5">
                  {intel.feature_highlights.map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-emerald-900">
                      <span className="material-symbols-outlined text-emerald-500 text-[14px] mt-0.5 shrink-0" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Objection responses */}
            {intel.objection_responses && Object.keys(intel.objection_responses).length > 0 && (
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-100">
                <p className="text-[10px] font-bold text-amber-600 uppercase tracking-wider mb-2">Handle Objections</p>
                {Object.entries(intel.objection_responses).map(([obj, resp]) => (
                  <div key={obj} className="mb-2 last:mb-0">
                    <p className="text-[10px] font-bold text-amber-800">"{obj}"</p>
                    <p className="text-xs text-amber-900 mt-0.5 leading-relaxed">{resp}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Follow-up timing */}
            {intel.follow_up_timing && (
              <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 p-2.5 rounded-lg">
                <span className="material-symbols-outlined text-[16px] text-slate-400">schedule</span>
                {intel.follow_up_timing}
              </div>
            )}
          </div>
        ) : (
          <p className="text-center text-slate-400 text-sm py-4">No intelligence data available.</p>
        )}

        {/* CTA */}
        <button
          onClick={onGenerateMessage}
          className="w-full flex items-center justify-center gap-2 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl transition-colors shadow-md shadow-blue-600/20"
        >
          <span className="material-symbols-outlined text-[18px]">outgoing_mail</span>
          Generate Outreach Email
        </button>
      </div>
    </div>
  );
}
