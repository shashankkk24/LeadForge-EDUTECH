import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import TopNavBar from './components/TopNavBar';
import KanbanBoard from './components/KanbanBoard';
import OutreachModal from './components/OutreachModal';
import IntelCard from './components/IntelCard';
import NewPipelineModal from './components/NewPipelineModal';
import { ScraperView, IntelligenceView, OutreachView, AnalyticsView } from './components/Views';
import { getLeads, triggerScrape } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

export default function App() {
  /* ── Global state ─────────────────────────────────────────────────────── */
  const [activeTab,              setActiveTab]              = useState('dashboard');
  const [leads,                  setLeads]                  = useState([]);
  const [loading,                setLoading]                = useState(true);
  const [isScraping,             setIsScraping]             = useState(false);
  const [scrapeCount,            setScrapeCount]            = useState(0);
  const [selectedLeadForIntel,   setSelectedLeadForIntel]   = useState(null);
  const [selectedLeadForOutreach,setSelectedLeadForOutreach]= useState(null);
  const [isNewPipelineModalOpen, setIsNewPipelineModalOpen] = useState(false);
  const [pipelines,              setPipelines]              = useState([
    { id: 1, name: 'Main Pipeline', keywords: 'edtech, school, education' },
  ]);

  const { messages, isConnected, clearMessages } = useWebSocket();

  /* ── Initial fetch ────────────────────────────────────────────────────── */
  const fetchLeads = useCallback(async () => {
    try {
      const data = await getLeads({ limit: 100 });
      setLeads(Array.isArray(data) ? data : data.leads || []);
    } catch (err) {
      console.error('Failed to fetch leads:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchLeads(); }, [fetchLeads]);

  /* ── WebSocket message handling ───────────────────────────────────────── */
  useEffect(() => {
    if (!messages.length) return;

    messages.forEach(msg => {
      switch (msg.type) {
        case 'JOB_STARTED':
          setIsScraping(true);
          setScrapeCount(0);
          break;

        case 'NEW_LEAD':
          if (msg.data) {
            setLeads(prev => prev.some(l => l.id === msg.data.id) ? prev : [msg.data, ...prev]);
            setScrapeCount(c => c + 1);
          }
          break;

        case 'JOB_COMPLETED':
          setIsScraping(false);
          fetchLeads();          // refresh from DB for full data
          break;

        case 'JOB_FAILED':
          setIsScraping(false);
          break;

        case 'LEAD_UPDATED':
          if (msg.data?.id) {
            setLeads(prev => prev.map(l => l.id === msg.data.id ? { ...l, ...msg.data } : l));
          }
          break;

        default: break;
      }
    });

    clearMessages();
  }, [messages, clearMessages, fetchLeads]);

  /* ── Actions ──────────────────────────────────────────────────────────── */
  const handleStartScrape = async (platform = 'reddit') => {
    if (isScraping) return;
    setIsScraping(true);
    setScrapeCount(0);
    try {
      await triggerScrape(platform);
    } catch (err) {
      console.error('Scrape trigger failed:', err);
      setIsScraping(false);
    }
  };

  const handleLeadClick    = lead => setSelectedLeadForIntel(lead);
  const handleOpenOutreach = lead => { setSelectedLeadForOutreach(lead); setSelectedLeadForIntel(null); };
  const handleUpdateLead   = updated => setLeads(prev => prev.map(l => l.id === updated.id ? { ...l, ...updated } : l));
  const handleAddPipeline  = p => setPipelines(prev => [...prev, { ...p, id: Date.now() }]);

  /* ── View router ──────────────────────────────────────────────────────── */
  const renderView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <KanbanBoard leads={leads} onLeadClick={handleLeadClick} loading={loading} />;
      case 'scraper':
        return <ScraperView leads={leads} isScraping={isScraping} scrapeCount={scrapeCount} onStartScrape={handleStartScrape} />;
      case 'intelligence':
        return <IntelligenceView leads={leads} onLeadClick={handleLeadClick} />;
      case 'outreach':
        return <OutreachView leads={leads} onLeadClick={handleOpenOutreach} />;
      case 'analytics':
        return <AnalyticsView leads={leads} />;
      default: return null;
    }
  };

  /* ── Render ───────────────────────────────────────────────────────────── */
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">

      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewPipeline={() => setIsNewPipelineModalOpen(true)}
        pipelines={pipelines}
        isConnected={isConnected}
      />

      {/* Main content */}
      <div className="flex flex-col flex-1 ml-64 min-w-0 overflow-hidden">
        <TopNavBar
          isScraping={isScraping}
          scrapeCount={scrapeCount}
          isConnected={isConnected}
          onScrapeNow={() => handleStartScrape('reddit')}
        />
        <main className="flex-1 overflow-hidden flex flex-col min-h-0">
          {renderView()}
        </main>
      </div>

      {/* Intel Card — fixed bottom-right overlay */}
      {selectedLeadForIntel && (
        <IntelCard
          lead={selectedLeadForIntel}
          onClose={() => setSelectedLeadForIntel(null)}
          onGenerateMessage={() => handleOpenOutreach(selectedLeadForIntel)}
        />
      )}

      {/* Outreach Modal */}
      {selectedLeadForOutreach && (
        <OutreachModal
          lead={selectedLeadForOutreach}
          onClose={() => setSelectedLeadForOutreach(null)}
          onUpdateLead={handleUpdateLead}
        />
      )}

      {/* New Pipeline Modal */}
      {isNewPipelineModalOpen && (
        <NewPipelineModal
          onClose={() => setIsNewPipelineModalOpen(false)}
          onAdd={handleAddPipeline}
        />
      )}
    </div>
  );
}
