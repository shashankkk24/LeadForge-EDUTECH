import React, { useState, useEffect } from 'react';
import { generateMessage, sendEmail, updateLeadStatus } from '../services/api';

const PRIORITY_BADGE = {
  HOT:  'bg-red-100 text-red-600',
  WARM: 'bg-orange-100 text-orange-600',
  COLD: 'bg-blue-100 text-blue-600',
};

export default function OutreachModal({ lead, onClose, onUpdateLead }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending,    setIsSending]    = useState(false);
  const [subject,      setSubject]      = useState('');
  const [body,         setBody]         = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');
  const [error,   setError]   = useState('');
  const [success, setSuccess] = useState('');

  /* Pre-fill if AI already generated */
  useEffect(() => {
    if (lead?.ai_subject) setSubject(lead.ai_subject);
    if (lead?.ai_message) setBody(lead.ai_message);
  }, [lead]);

  if (!lead) return null;

  const tags = Array.isArray(lead.pain_point_tags) ? lead.pain_point_tags : [];

  /* ── Generate with AI ── */
  const handleGenerate = async () => {
    setIsGenerating(true);
    setError('');
    setSuccess('');
    try {
      const data = await generateMessage(lead.id);
      setSubject(data.subject || '');
      setBody(data.body || '');
      onUpdateLead({ ...lead, ai_subject: data.subject, ai_message: data.body, status: 'Drafted' });
    } catch {
      setError('Failed to generate message. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  /* ── Send Email ── */
  const handleSend = async () => {
    if (!body.trim()) { setError('Please generate or write a message first.'); return; }
    setIsSending(true);
    setError('');
    setSuccess('');
    try {
      await sendEmail(lead.id, subject, body, recipientEmail);
      await updateLeadStatus(lead.id, 'Contacted');
      onUpdateLead({ ...lead, status: 'Contacted' });
      setSuccess('Email sent successfully!');
      setTimeout(onClose, 1500);
    } catch {
      setError('Failed to send email. Check SMTP configuration.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm p-4">
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl flex flex-col overflow-hidden max-h-[92vh]">

        {/* ── Header ── */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 bg-slate-50 shrink-0">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-blue-600 text-[22px]">outgoing_mail</span>
            <h2 className="font-black text-lg text-slate-900" style={{fontFamily:'Manrope,sans-serif'}}>AI Outreach Engine</h2>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-lg">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* ── Body ── */}
        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">

          {/* Lead summary */}
          <div className="flex items-center gap-3 bg-blue-50 border border-blue-100 rounded-xl p-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-blue-600 text-[22px]" style={{fontVariationSettings:"'FILL' 1"}}>person</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-slate-900">u/{lead.username}</p>
              <p className="text-xs text-slate-500 truncate">
                {lead.platform} · {lead.detected_role || 'Unknown role'} · {lead.urgency_level || 'low'} urgency
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className={`text-[10px] font-black px-2 py-1 rounded-full ${PRIORITY_BADGE[lead.priority] || 'bg-slate-100 text-slate-500'}`}>
                {lead.priority}
              </span>
              <span className="text-xs font-black text-slate-600 bg-slate-100 px-2 py-1 rounded-full">
                {lead.lead_score}/100
              </span>
            </div>
          </div>

          {/* Pain point tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {tags.map(tag => (
                <span key={tag} className="bg-slate-100 text-slate-600 text-[10px] font-semibold px-2 py-1 rounded-full">
                  #{tag.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          )}

          {/* Alerts */}
          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2.5 text-sm">
              <span className="material-symbols-outlined text-[18px] shrink-0">error</span>
              {error}
            </div>
          )}
          {success && (
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg px-3 py-2.5 text-sm">
              <span className="material-symbols-outlined text-[18px] shrink-0" style={{fontVariationSettings:"'FILL' 1"}}>check_circle</span>
              {success}
            </div>
          )}

          {/* Recipient email */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Recipient Email</label>
            <input
              type="email"
              value={recipientEmail}
              onChange={e => setRecipientEmail(e.target.value)}
              placeholder="prospect@school.edu  (leave blank to simulate)"
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          {/* Subject */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Subject Line</label>
            <input
              type="text"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              placeholder="Click Generate to create a personalized subject…"
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          {/* Body */}
          <div className="flex flex-col gap-1.5 flex-1">
            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Message Body</label>
            <textarea
              value={body}
              onChange={e => setBody(e.target.value)}
              placeholder="Click Generate to create a personalized message based on their pain points…"
              className="w-full border border-slate-300 rounded-lg px-3 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[180px] resize-y leading-relaxed"
            />
          </div>
        </div>

        {/* ── Footer ── */}
        <div className="flex items-center justify-between px-5 py-4 border-t border-slate-200 bg-slate-50 shrink-0">
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-lg font-semibold text-sm disabled:opacity-50"
          >
            <span className={`material-symbols-outlined text-[18px] text-blue-600 ${isGenerating ? 'animate-pulse' : ''}`}>
              auto_awesome
            </span>
            {isGenerating ? 'Generating…' : 'Generate with AI'}
          </button>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:bg-slate-200 rounded-lg font-semibold text-sm"
            >
              Cancel
            </button>
            <button
              onClick={handleSend}
              disabled={isSending || !body.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold text-sm shadow-md shadow-blue-600/20 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">send</span>
              {isSending ? 'Sending…' : 'Send Email'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
