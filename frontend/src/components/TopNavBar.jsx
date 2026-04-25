import React from 'react';

export default function TopNavBar({ isScraping, scrapeCount, isConnected, onScrapeNow }) {
  return (
    <header className="sticky top-0 z-30 h-16 flex items-center justify-between px-6 bg-white border-b border-slate-200 shrink-0">

      {/* Left — title + live badge */}
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-black text-slate-900" style={{fontFamily:'Manrope,sans-serif'}}>
          Pipeline Overview
        </h1>
        <div className="h-5 w-px bg-slate-200" />

        {isScraping ? (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs font-bold text-emerald-700 tracking-wide">
              Scraping… {scrapeCount} leads found
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-full">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-slate-400'}`} />
            <span className="text-xs font-semibold text-slate-500">
              {isConnected ? 'Live' : 'Idle'}
            </span>
          </div>
        )}
      </div>

      {/* Right — actions */}
      <div className="flex items-center gap-3">
        {/* Scrape Now */}
        <button
          onClick={onScrapeNow}
          disabled={isScraping}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-bold transition-colors shadow-sm shadow-blue-600/20"
        >
          <span className={`material-symbols-outlined text-[18px] ${isScraping ? 'animate-spin' : ''}`}>
            {isScraping ? 'sync' : 'radar'}
          </span>
          {isScraping ? 'Scraping…' : 'Scrape Now'}
        </button>

        {/* Search */}
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">search</span>
          <input
            className="pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm w-52 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            placeholder="Search leads…"
            type="text"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-lg">
          <span className="material-symbols-outlined text-[22px]">notifications</span>
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
        </button>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-black shadow-sm">
          L
        </div>
      </div>
    </header>
  );
}
