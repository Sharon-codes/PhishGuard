import { useState, useMemo } from 'react';
import axios from 'axios';
import './App.css';

/* ICONS */
const ShieldCheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>
);

const LoaderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-spin">
    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
  </svg>
);

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4Z"/>
    <path d="M22 2 11 13"/>
  </svg>
);

const InfoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 16v-4"/>
    <path d="M12 8h.01"/>
  </svg>
);

const AlertTriangleIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
    <path d="M12 9v4"/>
    <path d="M12 17h.01"/>
  </svg>
);

const SparklesIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
    <path d="M5 3v4"/>
    <path d="M19 17v4"/>
    <path d="M3 5h4"/>
    <path d="M17 19h4"/>
  </svg>
);

const BookOpenIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
  </svg>
);

const BadgeCheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3.85 8.62a4 4 0 0 1 4.78-4.78l1.21 1.22a1 1 0 0 0 1.42 0l1.21-1.22a4 4 0 0 1 4.78 4.78l-1.22 1.21a1 1 0 0 0 0 1.42l1.22 1.21a4 4 0 0 1-4.78 4.78l-1.21-1.22a1 1 0 0 0-1.42 0l-1.21 1.22a4 4 0 0 1-4.78-4.78l1.22-1.21a1 1 0 0 0 0-1.42z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>
);

const CopyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
  </svg>
);

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6 9 17l-5-5"/>
  </svg>
);

const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
  </svg>
);

const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const GlobeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
    <path d="M2 12h20"/>
  </svg>
);

const ZapIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>
  </svg>
);

function App() {
  const [text, setText] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const charCount = text.length;

  const samples = useMemo(() => ([
    'https://bit.ly/3abcXYZ',
    'Your bank account will be locked within 24 hours. Click https://bit.ly/3abcXYZ to verify.',
    'Win Rs 1,00,000! Claim at http://example-prize.xyz/claim?id=12345',
    'Hi, share your OTP to continue.',
    'Work from home opportunity! Apply now and earn $5000/month.'
  ]), []);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setResponse(null);
    setCopied(false);

    try {
      // Create request with new format
      const requestData = {
        raw_input: text,
        platform_hint: "other", // Could be enhanced with platform detection
        enrichment: {
          extracted_url: null,
          safe_browsing: { verdict: null, score: null, detail_url: null },
          virustotal: { malicious_count: null, suspicious_count: null, score: null, detail_url: null },
          urlscan: { verdict: null, screenshot_url: null, detail_url: null },
          whois: { created_date: null, age_days: null, registrar: null, abuse_contact: null },
          tls: { valid: null, certificate_subject: null, issuer: null, not_after: null },
          ct_logs: { matching_entries: null, latest_entry: null },
          dns: { resolved_ips: null, a_records_count: null, rbl_hits: null },
          ip_reputation: { is_malicious: null, source: null },
          domain_reputation_score: null,
          blacklist_matches: null,
          prior_scans_for_domain: null,
          sandbox: { performed: false, behavior_summary: null, downloads_detected: false, network_calls: null, screenshot_url: null }
        }
      };
      
      const res = await axios.post('/api/analyze', requestData);
      setResponse(res.data);
    } catch (err) {
      setError('Analysis failed. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    handleAnalyze();
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'HIGH':
        return 'risk-high';
      case 'MEDIUM':
        return 'risk-medium';
      case 'LOW':
        return 'risk-low';
      default:
        return '';
    }
  };

  const copyJson = async () => {
    if (!response) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Copy failed', e);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="brand">
            <div className="brand-icon">
              <ShieldCheckIcon />
            </div>
            <h1>PhishGuard Pro</h1>
          </div>
          <p className="header-subtitle">
            Advanced cybersecurity threat analysis powered by AI
          </p>
        </header>

        <section className="input-section">
          <div className="form-card">
            <form onSubmit={handleSubmit}>
              <div className="textarea-wrapper">
                <textarea
                  className="textarea"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Paste suspicious URLs, emails, or messages here for analysis..."
                  disabled={loading}
                />
              </div>
              <div className="form-footer">
                <div className="char-count">
                  {charCount.toLocaleString()} characters
                </div>
                <div className="form-actions">
                  <button
                    type="button"
                    className="button secondary"
                    onClick={() => setText('')}
                    disabled={loading || !text}
                  >
                    Clear
                  </button>
                  <button
                    type="submit"
                    className="button primary"
                    disabled={loading || !text.trim()}
                  >
                    {loading ? (
                      <>
                        <LoaderIcon />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <SendIcon />
                        Analyze Threat
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>

          <div className="samples">
            <span className="samples-label">Try these examples:</span>
            {samples.map((sample, index) => (
              <button
                key={index}
                className="chip"
                onClick={() => setText(sample)}
                disabled={loading}
              >
                {sample.length > 50 ? `${sample.slice(0, 50)}...` : sample}
              </button>
            ))}
          </div>
        </section>

        {error && (
          <div className="error">
            <AlertTriangleIcon />
            {error}
          </div>
        )}

        {response && (
          <section className="results">
            <div className="results-grid">
              <aside className="results-sidebar">
                <div className="risk-card">
                  <div className="risk-level">
                    <div className="risk-level-label">Threat Level</div>
                    <div className={`risk-badge ${getRiskColor(response.risk_level)}`}>
                      {response.risk_level}
                    </div>
                  </div>

                  <div className="final-score">
                    <div className="risk-level-label">Final Score</div>
                    <div className="final-score-value">{response.final_score}</div>
                  </div>

                  <div className="score-breakdown">
                    <div className="score-bar">
                      <div className="score-label">Heuristic</div>
                      <div className="score-progress">
                        <div
                          className="score-fill"
                          style={{ width: `${response.heuristic_score}%` }}
                        />
                      </div>
                      <div className="score-value">{response.heuristic_score}</div>
                    </div>
                    <div className="score-bar">
                      <div className="score-label">AI Analysis</div>
                      <div className="score-progress">
                        <div
                          className="score-fill"
                          style={{ width: `${response.llm_score}%` }}
                        />
                      </div>
                      <div className="score-value">{response.llm_score}</div>
                    </div>
                  </div>
                </div>
              </aside>

              <main className="results-content">
                <div className="card">
                  <div className="card-header">
                    <InfoIcon className="card-icon" />
                    <h2 className="card-title">Threat Overview</h2>
                  </div>
                  <div className="info-grid">
                    <div className="info-item">
                      <div className="info-label">Attack Type</div>
                      <div className="info-value">{response.attack_type}</div>
                    </div>
                    <div className="info-item">
                      <div className="info-label">Confidence Level</div>
                      <div className="info-value">{response.confidence_pct}%</div>
                    </div>
                    <div className="info-item">
                      <div className="info-label">Recommended Action</div>
                      <div className={`info-value pill ${response.action === 'BLOCK_CLICK' ? 'yes' : response.action === 'SAFE_TO_CLICK_AFTER_CHECKS' ? 'no' : 'medium'}`}>
                        {response.action.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>
                  {response.extracted_url && (
                    <div className="info-item">
                      <div className="info-label">Extracted URL</div>
                      <div className="info-value">{response.extracted_url}</div>
                    </div>
                  )}
                </div>

                <div className="card">
                  <div className="card-header">
                    <AlertTriangleIcon className="card-icon" />
                    <h2 className="card-title">Risk Indicators</h2>
                  </div>
                  <ul className="reasons-list">
                    {response.top_reasons.map((reason, index) => (
                      <li key={index} className="reason-item">
                        <AlertTriangleIcon className="reason-icon" />
                        <div className="reason-content">
                          <strong>{reason.reason}</strong>
                          <div className="evidence">
                            Evidence: "{reason.evidence}"
                          </div>
                          <div className="reason-meta">
                            <span className="reason-source">Source: {reason.source}</span>
                            {reason.weight && <span className="reason-weight">Weight: {reason.weight}</span>}
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="card">
                  <div className="card-header">
                    <SparklesIcon className="card-icon" />
                    <h2 className="card-title">Threat Analysis</h2>
                  </div>
                  <div className="explanation-content">
                    <SparklesIcon className="explanation-icon" />
                    <p>{response.attacker_intent_explanation}</p>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <BookOpenIcon className="card-icon" />
                    <h2 className="card-title">Security Recommendations</h2>
                  </div>
                  <div className="actions-grid">
                    <div className="action-card suggested">
                      <div className="action-header">
                        <BadgeCheckIcon className="action-icon" />
                        Immediate Action
                      </div>
                      <div className="action-content">
                        {response.suggested_action_text}
                      </div>
                    </div>
                    <div className="action-card education">
                      <div className="action-header">
                        <BookOpenIcon className="action-icon" />
                        Security Tip
                      </div>
                      <div className="action-content">
                        {response.education_tip}
                      </div>
                    </div>
                  </div>
                </div>
              </main>
            </div>

            <div className="toolbar">
              <button className="button secondary" onClick={copyJson}>
                {copied ? (
                  <>
                    <CheckIcon />
                    Copied!
                  </>
                ) : (
                  <>
                    <CopyIcon />
                    Export JSON
                  </>
                )}
              </button>
            </div>

            {response.note && (
              <div className="note">
                <strong>Note:</strong> {response.note}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}

export default App;