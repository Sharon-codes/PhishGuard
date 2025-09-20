import re
import json
from urllib.parse import urlparse, parse_qs
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from ai_service import gemini_service
from url_resolver import url_resolver

app = Flask(__name__)

# Configure CORS for production and development
CORS(app, origins=["*"])  # Will be updated after deployment

def extract_url_and_message(raw_input):
    """Extract URL from raw input if not provided in enrichment"""
    url_pattern = r'https?://[^\s/$.?#].[^\s]*|www\.[^\s/$.?#].[^\s]*|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[/\S]*)'
    urls = re.findall(url_pattern, raw_input)
    
    extracted_url = urls[0] if urls else None
    multiple_urls = len(urls) > 1
    message_text = "" if (extracted_url and raw_input.strip() == extracted_url.strip()) else raw_input
    
    return extracted_url, message_text, multiple_urls

def redact_pii(text):
    """Redact PII from text"""
    if not text:
        return ""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    
    redacted_text = re.sub(email_pattern, '[EMAIL_REDACTED]', text)
    redacted_text = re.sub(phone_pattern, '[PHONE_REDACTED]', redacted_text)
    
    return redacted_text

def calculate_heuristic_score(raw_input, extracted_url, enrichment, platform_hint=None):
    """Calculate heuristic score based on deterministic rules"""
    base_score = 0
    evidence_sources = []
    
    # URL/Enrichment rules
    if extracted_url is None:
        base_score += 0  # No URL evidence
    
    # Safe browsing
    safe_browsing = enrichment.get('safe_browsing', {})
    if safe_browsing.get('verdict') == 'MALICIOUS':
        base_score += 60
        evidence_sources.append(('safe_browsing', 60))
    elif safe_browsing.get('verdict') == 'SUSPICIOUS':
        base_score += 30
        evidence_sources.append(('safe_browsing', 30))
    
    # VirusTotal
    virustotal = enrichment.get('virustotal', {})
    malicious_count = virustotal.get('malicious_count') or 0
    if malicious_count > 0:
        vt_score = 10 * min(10, malicious_count)
        base_score += vt_score
        evidence_sources.append(('virustotal', vt_score))
    
    # URLScan
    urlscan = enrichment.get('urlscan', {})
    if urlscan.get('verdict') == 'malicious':
        base_score += 40
        evidence_sources.append(('urlscan', 40))
    
    # WHOIS age
    whois = enrichment.get('whois', {})
    age_days = whois.get('age_days')
    if age_days is not None and age_days < 90:
        base_score += 20
        evidence_sources.append(('whois', 20))
    
    # TLS
    tls = enrichment.get('tls', {})
    if tls.get('valid') is False:
        base_score += 25
        evidence_sources.append(('tls', 25))
    
    # CT Logs
    ct_logs = enrichment.get('ct_logs', {})
    matching_entries = ct_logs.get('matching_entries') or 0
    if matching_entries > 5:
        base_score -= 10
        evidence_sources.append(('ct_logs', -10))
    
    # Domain reputation
    domain_reputation_score = enrichment.get('domain_reputation_score')
    if domain_reputation_score is not None:
        domain_score = min(40, max(0, domain_reputation_score))
        base_score += domain_score
        evidence_sources.append(('domain_reputation', domain_score))
    
    # Blacklist matches
    blacklist_matches = enrichment.get('blacklist_matches', []) or []
    if blacklist_matches:
        base_score += 50
        evidence_sources.append(('blacklist', 50))
    
    # IP reputation
    ip_reputation = enrichment.get('ip_reputation', {})
    if ip_reputation.get('is_malicious'):
        base_score += 40
        evidence_sources.append(('ip_reputation', 40))
    
    # Heuristic URL patterns (if enrichment data null or to supplement)
    if extracted_url:
        shorteners = ['bit.ly', 't.co', 'tinyurl.com', 'ow.ly', 'buff.ly', 'shorturl.at', 'is.gd', 'goo.gl', 'rb.gy']
        parsed = urlparse(extracted_url if extracted_url.startswith(('http://', 'https://')) else f'http://{extracted_url}')
        hostname = parsed.hostname or ''
        
        if any(s in hostname for s in shorteners):
            # Reduce the score for URL shorteners - they might be legitimate marketing
            base_score += 15  # Reduced from 25
            evidence_sources.append(('raw_input', 15))
        
        if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', hostname) or hostname.startswith('[') and hostname.endswith(']'):
            base_score += 20
            evidence_sources.append(('raw_input', 20))
        
        if 'xn--' in hostname:
            base_score += 25
            evidence_sources.append(('raw_input', 25))
        
        typos = ['g00gle', 'faceb00k', 'micros0ft', 'amaz0n', 'paypa1']
        if any(t in hostname for t in typos):
            base_score += 40
            evidence_sources.append(('raw_input', 40))
        
        suspicious_tlds = ['.xyz', '.top', '.pw', '.loan', '.buzz']
        if any(hostname.endswith(tld) for tld in suspicious_tlds):
            base_score += 10
            evidence_sources.append(('raw_input', 10))
        
        if len(parsed.path) > 120 or len(parse_qs(parsed.query)) > 5:
            base_score += 8
            evidence_sources.append(('raw_input', 8))
    
    # Message heuristics
    if raw_input:
        if re.search(r'\b(immediately|urgent|within 24 hours)\b', raw_input, re.IGNORECASE):
            base_score += 15
            evidence_sources.append(('raw_input', 15))
        
        if re.search(r'\b(OTP|one time password|password|PIN)\b', raw_input, re.IGNORECASE):
            base_score += 35
            evidence_sources.append(('raw_input', 35))
        
        if re.search(r'\b(money|lottery|prize|transfer)\b', raw_input, re.IGNORECASE):
            base_score += 25
            evidence_sources.append(('raw_input', 25))
        
        if re.search(r'\b(account blocked|suspended|legal action)\b', raw_input, re.IGNORECASE):
            base_score += 20
            evidence_sources.append(('raw_input', 20))
        
        if re.search(r'\b(click here|verify now)\b', raw_input, re.IGNORECASE):
            base_score += 10
            evidence_sources.append(('raw_input', 10))
        
        if re.search(r'\b(work from home)\b', raw_input, re.IGNORECASE) and re.search(r'\b(pay first|upfront fee)\b', raw_input, re.IGNORECASE):
            base_score += 20
            evidence_sources.append(('raw_input', 20))
    
    # Sandbox signals
    sandbox = enrichment.get('sandbox', {})
    if sandbox.get('performed'):
        behavior = sandbox.get('behavior_summary', '') or ''
        if any(word in behavior.lower() for word in ['download', 'spawned process', 'crypto-miner']):
            base_score += 60
            evidence_sources.append(('sandbox', 60))
        elif 'harmless static content' in behavior.lower():
            base_score -= 15
            evidence_sources.append(('sandbox', -15))
    
    # Context signals
    if platform_hint in ['sms', 'whatsapp'] and extracted_url and any(s in extracted_url for s in ['bit.ly', 't.co']):
        base_score += 10
        evidence_sources.append(('raw_input', 10))
    
    prior_scans = enrichment.get('prior_scans_for_domain') or 0
    if prior_scans > 10:
        base_score += 30
        evidence_sources.append(('domain_reputation', 30))
    
    # Clamp and normalize
    base_score = max(0, min(200, base_score))
    heuristic_score = min(100, round(base_score / 2))
    
    return heuristic_score, evidence_sources

def get_ai_reasoning(redacted_message, extracted_url, enrichment, url_resolution=None):
    """Get AI-powered reasoning using Gemini AI"""
    try:
        # Use Gemini AI service for analysis
        ai_result = gemini_service.analyze_phishing_content(
            message_content=redacted_message,
            extracted_url=extracted_url,
            enrichment_data=enrichment,
            url_resolution=url_resolution
        )
        
        # Convert AI result to expected format
        return {
            "attack_type": ai_result.get('attack_type', 'UNKNOWN'),
            "llm_score": ai_result.get('confidence_score', 0),
            "confidence_pct": ai_result.get('confidence_score', 0),
            "top_reasons": [
                {
                    "reason": indicator.get('description', ''),
                    "evidence": redacted_message[:100] if redacted_message else extracted_url or 'No evidence',
                    "source": indicator.get('type', 'ai_analysis'),
                    "weight": indicator.get('confidence', 0) // 2  # Convert to weight scale
                }
                for indicator in ai_result.get('indicators', [])[:3]
            ],
            "attacker_intent_explanation": ai_result.get('attacker_intent', 'Unable to determine intent'),
            "ai_reasoning": ai_result.get('reasoning', 'No detailed reasoning available'),
            "recommended_action": ai_result.get('recommended_action', 'VERIFY'),
            "risk_level": ai_result.get('risk_level', 'LOW'),
            "is_ai_powered": gemini_service.enabled
        }
        
    except Exception as e:
        print(f"Error in AI reasoning: {str(e)}")
        # Fallback to basic analysis
        return {
            "attack_type": "UNKNOWN",
            "llm_score": 15,
            "confidence_pct": 40,
            "top_reasons": [{
                "reason": "AI analysis unavailable, using basic detection",
                "evidence": redacted_message[:100] if redacted_message else "No content",
                "source": "fallback",
                "weight": 10
            }],
            "attacker_intent_explanation": "Unable to determine without AI analysis",
            "ai_reasoning": "AI service unavailable",
            "recommended_action": "VERIFY",
            "risk_level": "LOW",
            "is_ai_powered": False
        }

def determine_action(final_score, safe_browsing_verdict, blacklist_matches, platform_hint):
    """Determine definitive action based on score and evidence"""
    high_confidence_malicious = (
        safe_browsing_verdict == "MALICIOUS" or 
        (blacklist_matches and any(source in str(blacklist_matches) for source in ['phishtank', 'openphish']))
    )
    
    if final_score >= 85 or high_confidence_malicious:
        return "BLOCK_CLICK"
    elif final_score >= 70:
        return "QUARANTINE_EMAIL" if platform_hint == "email" else "BLOCK_CLICK"
    elif 50 <= final_score < 70:
        return "VERIFY_VIA_KNOWN_CHANNEL"
    elif 30 <= final_score < 50:
        return "SANDBOX_ANALYZE"
    else:
        return "SAFE_TO_CLICK_AFTER_CHECKS"

def build_provenance(enrichment):
    """Build provenance array from enrichment data"""
    provenance = []
    
    safe_browsing = enrichment.get('safe_browsing', {})
    if safe_browsing.get('verdict'):
        provenance.append({
            "signal": "safe_browsing",
            "value": safe_browsing.get('verdict'),
            "detail_url": safe_browsing.get('detail_url')
        })
    
    virustotal = enrichment.get('virustotal', {})
    if virustotal.get('malicious_count') is not None:
        provenance.append({
            "signal": "virustotal",
            "malicious_count": virustotal.get('malicious_count'),
            "detail_url": virustotal.get('detail_url')
        })
    
    urlscan = enrichment.get('urlscan', {})
    if urlscan.get('verdict'):
        provenance.append({
            "signal": "urlscan",
            "value": urlscan.get('verdict'),
            "detail_url": urlscan.get('detail_url'),
            "screenshot_url": urlscan.get('screenshot_url')
        })
    
    return provenance

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'raw_input' not in data:
        return jsonify({"error": "No raw_input provided"}), 400

    raw_input = data.get('raw_input', '')
    platform_hint = data.get('platform_hint')
    enrichment = data.get('enrichment', {})
    
    # Extract URL if not provided in enrichment
    extracted_url = enrichment.get('extracted_url')
    if not extracted_url:
        extracted_url, message_text, multiple_urls = extract_url_and_message(raw_input)
    else:
        _, message_text, multiple_urls = extract_url_and_message(raw_input)
    
    # Redact PII
    redacted_message = redact_pii(message_text)
    redacted_url = redact_pii(extracted_url) if extracted_url else None
    
    # Resolve URL if it's a shortened URL
    url_resolution = None
    marketing_analysis = None
    
    if extracted_url and url_resolver.is_shortened_url(extracted_url):
        try:
            print(f"Resolving shortened URL: {extracted_url}")
            url_resolution = url_resolver.resolve_url(extracted_url)
            marketing_analysis = url_resolver.analyze_marketing_legitimacy(url_resolution, raw_input)
            print(f"URL resolved to: {url_resolution.get('final_url', 'N/A')}")
            print(f"Marketing analysis: {marketing_analysis.get('is_likely_marketing', False)}")
        except Exception as e:
            print(f"Error resolving URL: {str(e)}")
            url_resolution = {"error": str(e)}
    
    # Calculate scores
    heuristic_score, evidence_sources = calculate_heuristic_score(raw_input, extracted_url, enrichment, platform_hint)
    
    # Override heuristic score if this is a legitimate marketing link
    if marketing_analysis and marketing_analysis.get('is_likely_marketing', False):
        print(f"[Marketing Override] Reducing heuristic score for legitimate marketing link")
        heuristic_score = min(heuristic_score, 30)  # Cap at 30 for marketing links
    
    ai_result = get_ai_reasoning(redacted_message, redacted_url, enrichment, url_resolution)
    
    # Fuse scores (use AI risk level if available, otherwise use score-based calculation)
    if ai_result.get('is_ai_powered', False):
        # Use AI-determined risk level and score
        ai_risk_level = ai_result.get('risk_level', 'LOW')
        ai_score = ai_result['llm_score']
        
        # Blend heuristic and AI scores, giving more weight to AI when available
        final_score = round(min(100, 0.3 * heuristic_score + 0.7 * ai_score))
        risk_level = ai_risk_level
    else:
        # Fallback to original scoring method
        final_score = round(min(100, 0.55 * heuristic_score + 0.45 * ai_result['llm_score']))
        
        # Determine risk level
        if final_score >= 70:
            risk_level = "HIGH"
        elif final_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
    
    # Determine action (consider AI recommendation if available)
    if ai_result.get('is_ai_powered', False) and ai_result.get('recommended_action'):
        ai_action = ai_result['recommended_action']
        action_mapping = {
            "BLOCK": "BLOCK_CLICK",
            "QUARANTINE": "QUARANTINE_EMAIL",
            "VERIFY": "VERIFY_VIA_KNOWN_CHANNEL",
            "CAUTION": "SANDBOX_ANALYZE",
            "ALLOW": "SAFE_TO_CLICK_AFTER_CHECKS"
        }
        action = action_mapping.get(ai_action, determine_action(
            final_score,
            enrichment.get('safe_browsing', {}).get('verdict'),
            enrichment.get('blacklist_matches'),
            platform_hint
        ))
    else:
        action = determine_action(
            final_score,
            enrichment.get('safe_browsing', {}).get('verdict'),
            enrichment.get('blacklist_matches'),
            platform_hint
        )
    
    # Build response
    response = {
        "final_score": final_score,
        "heuristic_score": heuristic_score,
        "llm_score": ai_result['llm_score'],
        "ai_score": ai_result['llm_score'],
        "risk_level": risk_level,
        "action": action,
        "confidence_pct": ai_result['confidence_pct'],
        "attack_type": ai_result['attack_type'],
        "extracted_url": redacted_url,
        "multiple_urls": multiple_urls,
        "top_reasons": ai_result['top_reasons'],
        "provenance": build_provenance(enrichment),
        "attacker_intent_explanation": ai_result['attacker_intent_explanation'],
        "ai_reasoning": ai_result.get('ai_reasoning', 'No AI reasoning available'),
        "is_ai_powered": ai_result.get('is_ai_powered', False),
        "url_resolution": url_resolution,
        "marketing_analysis": marketing_analysis,
        "suggested_action_text": {
            "BLOCK_CLICK": "Do NOT click this link. Block access immediately.",
            "QUARANTINE_EMAIL": "Move this email to quarantine. Do not interact with any links or attachments.",
            "VERIFY_VIA_KNOWN_CHANNEL": "Verify this request through official channels before taking any action.",
            "SANDBOX_ANALYZE": "Analyze in a secure sandbox environment before accessing.",
            "SAFE_TO_CLICK_AFTER_CHECKS": "Exercise normal caution when accessing this content."
        }.get(action, "Review manually before proceeding."),
        "marketing_notice": "This appears to be a legitimate marketing link" if ai_result.get('attack_type') == 'MARKETING_LINK' else None,
        "automation_advice": {
            "can_automate": action in ["BLOCK_CLICK", "QUARANTINE_EMAIL"],
            "recommended_actions": [
                {
                    "action": "block_url" if action == "BLOCK_CLICK" else "quarantine_email",
                    "required_consent": "admin" if final_score >= 85 else "user",
                    "confidence_required_pct": 85 if action == "BLOCK_CLICK" else 70
                }
            ] if action in ["BLOCK_CLICK", "QUARANTINE_EMAIL"] else []
        },
        "education_tip": "Always verify suspicious requests through official channels. This tool is educational and is not a replacement for official incident response.",
        "note": "Analysis includes enrichment data when available" + ("; multiple URLs detected" if multiple_urls else "")
    }

    return jsonify(response)

@app.route('/api/education/<attack_type>', methods=['GET'])
def get_education(attack_type):
    """Get educational content about specific attack types"""
    try:
        education_content = gemini_service.get_educational_content(attack_type.upper())
        return jsonify({
            "attack_type": attack_type.upper(),
            "education": education_content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get education content: {str(e)}"}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get service status including AI availability"""
    return jsonify({
        "service": "PhishGuard API",
        "status": "running",
        "ai_enabled": gemini_service.enabled,
        "ai_service": "Google Gemini" if gemini_service.enabled else "Disabled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0-ai"
    })

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler"""
    return app

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5001)