import React, { useState } from 'react';

/* ─────────────────────────────────────────────────────────────────────────────
   A. SCRAPER VIEW
───────────────────────────────────────────────────────────────────────────── */
export function ScraperView({ leads, isScraping, scrapeCount, onStartScrape }) {
  const [platform, setPlatform] = useState('reddit');

  const recent = [...leads]
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 15);

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-8">
      <div className="max-w-5xl mx-auto">

        <h1 className="text-2xl font-black text-slate-900 mb-1" style={{fontFamily:'Manrope,sans-serif'}}>Lead Scraper</h1>
        <p className="text-sm text-slate-500 mb-8">Scrape Reddit for high-intent EdTech leads in real time.</p>

        {/* ── Control card ── */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
          <div className="flex items-start justify-between gap-6">
            <div className="flex-1">
              <h2 className="font-bold text-lg text-slate-900 mb-1" style={{fontFamily:'Manrope,sans-serif'}}>Run Scraper</h2>
              <p className="text-sm text-slate-500 mb-5">
                Fetches posts from r/edtech, r/education, r/Teachers, r/k12sysadmin and filters by EdTech keywords.
              </p>
              <div className="flex items-end gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Platform</label>
                  <select
                    value={platform}
                    onChange={e => setPlatform(e.target.value)}
                    className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 outline-none focus:border-blue-500"
                  >
                    <option value="reddit">Reddit (Public JSON API)</option>
                  </select>
                </div>
                <button
                  onClick={() => onStartScrape(platform)}
                  disabled={isScraping}
                  className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-bold text-sm shadow-md shadow-blue-600/20"
                >
                  <span className={`material-symbols-outlined text-[18px] ${isScraping ? 'animate-spin' : ''}`}>
                    {isScraping ? 'sync' : 'radar'}
                  </span>
                  {isScraping ? 'Scraping…' : 'Scrape Now'}
                </button>
              </div>
            </div>

            {/* Live counter */}
            <div className={`flex flex-col items-center justify-center w-32 h-28 rounded-2xl border-2 shrink-0 ${
              isScraping ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200 bg-slate-50'
            }`}>
              <span className={`text-4xl font-black ${isScraping ? 'text-emerald-600' : 'text-slate-400'}`}>
                {scrapeCount}
              </span>
              <span className="text-xs font-bold text-slate-500 mt-1">
                {isScraping ? 'leads found' : 'last run'}
              </span>
              {isScraping && (
                <div className="flex gap-1 mt-2">
                  {[0,1,2].map(i => (
                    <div key={i} className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"
                      style={{animationDelay:`${i*0.15}s`}} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Recent leads table ── */}
        <h2 className="text-lg font-bold text-slate-900 mb-4" style={{fontFamily:'Manrope,sans-serif'}}>Recently Scraped Leads</h2>
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {['Username','Role','Priority','Score','Intent','Post'].map(h => (
                  <th key={h} className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recent.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-slate-400 text-sm">
                    No leads yet — click "Scrape Now" to start.
                  </td>
                </tr>
              ) : recent.map(lead => (
                <tr key={lead.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                  <td className="px-4 py-3 font-semibold text-sm text-slate-900">u/{lead.username || 'anon'}</td>
                  <td className="px-4 py-3 text-sm text-slate-500 capitalize">{lead.detected_role || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] font-black px-2 py-1 rounded-full ${
                      lead.priority === 'HOT'  ? 'bg-red-100 text-red-600' :
                      lead.priority === 'WARM' ? 'bg-orange-100 text-orange-600' :
                                                 'bg-blue-100 text-blue-600'
                    }`}>{lead.priority || 'COLD'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${
                          (lead.lead_score||0) >= 70 ? 'bg-red-500' :
                          (lead.lead_score||0) >= 40 ? 'bg-orange-400' : 'bg-blue-400'
                        }`} style={{width:`${lead.lead_score||0}%`}} />
                      </div>
                      <span className="text-xs font-bold text-slate-600">{lead.lead_score||0}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-1 rounded">
                      {lead.intent_label?.replace(/_/g,' ') || '—'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {lead.post_url
                      ? <a href={lead.post_url} target="_blank" rel="noopener noreferrer"
                           className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-xs font-semibold">
                          View <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                        </a>
                      : <span className="text-slate-300 text-xs">—</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
   B. INTELLIGENCE VIEW
───────────────────────────────────────────────────────────────────────────── */
export function IntelligenceView({ leads, onLeadClick }) {
  const enriched = leads.filter(l => l.pain_point_tags?.length > 0 || l.intent_label);

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-black text-slate-900 mb-1" style={{fontFamily:'Manrope,sans-serif'}}>Lead Intelligence</h1>
        <p className="text-sm text-slate-500 mb-8">AI-extracted insights for every prospect. Click a card to open the full intelligence panel.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {enriched.length > 0 ? enriched.map(lead => {
            const tags = Array.isArray(lead.pain_point_tags) ? lead.pain_point_tags : [];
            return (
              <div
                key={lead.id}
                onClick={() => onLeadClick(lead)}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 cursor-pointer hover:border-blue-400 hover:shadow-md hover:-translate-y-0.5 transition-all"
              >
                {/* Header */}
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-bold text-sm text-slate-900">u/{lead.username}</h3>
                    <p className="text-xs text-slate-500 capitalize mt-0.5">{lead.detected_role || 'Unknown'} · {lead.platform}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                      lead.priority === 'HOT'  ? 'bg-red-100 text-red-600' :
                      lead.priority === 'WARM' ? 'bg-orange-100 text-orange-600' :
                                                 'bg-blue-100 text-blue-600'
                    }`}>{lead.priority}</span>
                    <span className="text-xs font-black text-slate-700">{lead.lead_score}/100</span>
                  </div>
                </div>

                {/* Intent */}
                {lead.intent_label && (
                  <div className="mb-3">
                    <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 px-2 py-1 rounded">
                      {lead.intent_label.replace(/_/g,' ')}
                    </span>
                  </div>
                )}

                {/* Tags */}
                {tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {tags.slice(0,3).map(tag => (
                      <span key={tag} className="bg-slate-100 text-slate-600 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                        #{tag.replace(/_/g,' ')}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content preview */}
                <p className="text-xs text-slate-500 line-clamp-2 mb-3 leading-relaxed">{lead.post_content}</p>

                <button className="flex items-center gap-1 text-blue-600 text-xs font-bold hover:text-blue-800">
                  View Intelligence <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                </button>
              </div>
            );
          }) : (
            <div className="col-span-full py-16 text-center bg-white rounded-2xl border-2 border-dashed border-slate-200 text-slate-400">
              <span className="material-symbols-outlined text-5xl mb-3 block">psychology</span>
              <p className="font-semibold">No enriched leads yet.</p>
              <p className="text-sm mt-1">Scrape some leads first to see AI intelligence here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
   C. OUTREACH VIEW
───────────────────────────────────────────────────────────────────────────── */
export function OutreachView({ leads, onLeadClick }) {
  const outreachLeads = leads.filter(l => l.status === 'Drafted' || l.status === 'Contacted');

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-black text-slate-900 mb-1" style={{fontFamily:'Manrope,sans-serif'}}>Outreach Hub</h1>
        <p className="text-sm text-slate-500 mb-8">Manage drafted emails and track sent outreach.</p>

        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          {outreachLeads.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {outreachLeads.map(lead => (
                <div key={lead.id} className="flex items-center justify-between p-5 hover:bg-slate-50">
                  <div className="flex items-center gap-4">
                    <div className="w-11 h-11 rounded-xl bg-slate-100 flex items-center justify-center text-lg font-black text-slate-500">
                      {(lead.username||'?').charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold text-sm text-slate-900">u/{lead.username}</p>
                      <p className="text-xs text-slate-500">{lead.platform} · {lead.detected_role || 'Unknown'}</p>
                      {lead.ai_subject && (
                        <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xs">"{lead.ai_subject}"</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      lead.status === 'Contacted' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                    }`}>{lead.status}</span>
                    <button
                      onClick={() => onLeadClick(lead)}
                      className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold text-xs"
                    >
                      {lead.status === 'Drafted' ? 'Review & Send' : 'View Email'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center">
              <span className="material-symbols-outlined text-5xl text-slate-300 mb-3 block">forward_to_inbox</span>
              <h3 className="font-bold text-slate-600 mb-1">No active outreach</h3>
              <p className="text-sm text-slate-400">Generate emails from the Dashboard or Intelligence view.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
   D. ANALYTICS VIEW
───────────────────────────────────────────────────────────────────────────── */
export function AnalyticsView({ leads }) {
  const total     = leads.length;
  const hot       = leads.filter(l => l.priority === 'HOT').length;
  const warm      = leads.filter(l => l.priority === 'WARM').length;
  const cold      = leads.filter(l => l.priority === 'COLD').length;
  const contacted = leads.filter(l => l.status === 'Contacted').length;
  const closed    = leads.filter(l => l.status === 'Closed').length;
  const avgScore  = total ? Math.round(leads.reduce((s,l) => s+(l.lead_score||0),0)/total) : 0;
  const convRate  = total ? Math.round((contacted/total)*100) : 0;

  const intentCounts = leads.reduce((acc,l) => {
    const k = l.intent_label || 'UNKNOWN';
    acc[k] = (acc[k]||0)+1;
    return acc;
  }, {});

  const STATS = [
    { label:'Total Leads',     value:total,          icon:'group',               color:'text-blue-600',   bg:'bg-blue-50'   },
    { label:'HOT Leads',       value:hot,            icon:'local_fire_department',color:'text-red-600',    bg:'bg-red-50'    },
    { label:'Avg HeatScore',   value:`${avgScore}/100`,icon:'bolt',              color:'text-purple-600', bg:'bg-purple-50' },
    { label:'Contacted',       value:contacted,      icon:'mark_email_read',     color:'text-emerald-600',bg:'bg-emerald-50'},
    { label:'Conversion Rate', value:`${convRate}%`, icon:'trending_up',         color:'text-amber-600',  bg:'bg-amber-50'  },
    { label:'Closed',          value:closed,         icon:'check_circle',        color:'text-slate-600',  bg:'bg-slate-100' },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-black text-slate-900 mb-1" style={{fontFamily:'Manrope,sans-serif'}}>Performance Analytics</h1>
        <p className="text-sm text-slate-500 mb-8">Pipeline metrics and lead quality breakdown.</p>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {STATS.map(s => (
            <div key={s.label} className={`${s.bg} p-4 rounded-2xl border border-white/60 shadow-sm`}>
              <span className={`material-symbols-outlined text-[22px] ${s.color} mb-2 block`} style={{fontVariationSettings:"'FILL' 1"}}>{s.icon}</span>
              <p className={`text-2xl font-black ${s.color}`} style={{fontFamily:'Manrope,sans-serif'}}>{s.value}</p>
              <p className="text-xs text-slate-500 font-medium mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Priority breakdown */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 mb-5" style={{fontFamily:'Manrope,sans-serif'}}>Priority Breakdown</h3>
            <div className="flex flex-col gap-4">
              {[
                { label:'HOT',  count:hot,  bar:'bg-red-500',    text:'text-red-600'    },
                { label:'WARM', count:warm, bar:'bg-orange-400', text:'text-orange-600' },
                { label:'COLD', count:cold, bar:'bg-blue-400',   text:'text-blue-600'   },
              ].map(p => (
                <div key={p.label} className="flex items-center gap-3">
                  <span className={`text-xs font-black w-10 ${p.text}`}>{p.label}</span>
                  <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${p.bar}`}
                      style={{width: total > 0 ? `${(p.count/total)*100}%` : '0%'}} />
                  </div>
                  <span className="text-xs font-bold text-slate-600 w-6 text-right">{p.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Intent distribution */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-slate-900 mb-5" style={{fontFamily:'Manrope,sans-serif'}}>Intent Distribution</h3>
            <div className="flex flex-col gap-2.5">
              {Object.entries(intentCounts).length > 0
                ? Object.entries(intentCounts)
                    .sort((a,b) => b[1]-a[1])
                    .map(([intent, count]) => (
                      <div key={intent} className="flex items-center justify-between">
                        <span className="text-xs text-slate-600 font-medium">{intent.replace(/_/g,' ')}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-400 rounded-full"
                              style={{width: total > 0 ? `${(count/total)*100}%` : '0%'}} />
                          </div>
                          <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded-full w-6 text-center">{count}</span>
                        </div>
                      </div>
                    ))
                : <p className="text-sm text-slate-400">No data yet.</p>
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
