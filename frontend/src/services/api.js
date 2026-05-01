import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE_URL });

// ── Leads ─────────────────────────────────────────────────────────────────────

export const getLeads = async (params = {}) => {
  const response = await api.get('/leads', { params });
  return response.data; // { total, page, page_size, leads: [] }
};

export const getLead = async (id) => {
  const response = await api.get(`/leads/${id}`);
  return response.data;
};

export const updateLeadStatus = async (id, status) => {
  const response = await api.patch(`/leads/${id}`, { status });
  return response.data;
};

export const updateLead = async (id, data) => {
  const response = await api.patch(`/leads/${id}`, data);
  return response.data;
};

export const deleteLead = async (id) => {
  const response = await api.delete(`/leads/${id}`);
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get('/leads/stats');
  return response.data;
};

// ── Scraper ───────────────────────────────────────────────────────────────────

export const triggerScrape = async (platform = 'reddit', keywords = []) => {
  const defaultKeywords = [
    'school ERP',
    'LMS recommendation',
    'grading system',
    'attendance software',
    'school management software',
  ];
  const response = await api.post('/scrape', {
    platform,
    keywords: keywords.length > 0 ? keywords : defaultKeywords,
  });
  return response.data;
};

export const getScrapeJob = async (jobId) => {
  const response = await api.get(`/scrape/jobs/${jobId}`);
  return response.data;
};

// ── Outreach ──────────────────────────────────────────────────────────────────

export const generateMessage = async (id) => {
  const response = await api.post(`/outreach/generate-message/${id}`);
  return response.data; // { subject, body, confidence }
};

export const sendEmail = async (id, subject, body, recipientEmail = '') => {
  const response = await api.post(`/outreach/send-email/${id}`, {
    lead_id: id,
    recipient_email: recipientEmail || 'prospect@example.com',
    subject,
    body,
  });
  return response.data;
};

export const getLeadIntelligence = async (id) => {
  const response = await api.get(`/outreach/intelligence/${id}`);
  return response.data;
};

export const getOutreachLogs = async (id) => {
  const response = await api.get(`/outreach/logs/${id}`);
  return response.data;
};
