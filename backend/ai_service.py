"""
AI Service Module for PhishGuard
Integrates Google Gemini AI for advanced phishing detection
"""

import os
import json
from dotenv import load_dotenv

# Optional import: make Google Generative AI dependency optional in prod
try:
    import google.generativeai as genai  # type: ignore
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore
    _GENAI_AVAILABLE = False
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()

class GeminiAIService:
    """Service class for Google Gemini AI integration"""
    
    def __init__(self):
        """Initialize the Gemini AI service"""
        try:
            # If SDK missing, disable AI cleanly
            if not _GENAI_AVAILABLE:
                print("google-generativeai not installed. AI features disabled.")
                self.enabled = False
                return

            # Disable AI when running on Vercel unless explicitly enabled
            if os.getenv('VERCEL', '').lower() in ('1', 'true', 'yes') and os.getenv('ENABLE_GEMINI_AI', 'false').lower() not in ('1','true','yes'):
                print("Running on Vercel without ENABLE_GEMINI_AI=true. Disabling AI to avoid latency/timeouts.")
                self.enabled = False
                return

            self.api_key = os.getenv('GEMINI_API_KEY')
            if not self.api_key or self.api_key == 'your_gemini_api_key_here':
                print("Warning: GEMINI_API_KEY not set or using placeholder. AI features will be disabled.")
                print("Please set your actual Gemini API key in the .env file")
                self.enabled = False
                return
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            print("Gemini AI service initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini AI: {str(e)}")
            print("AI features will be disabled, falling back to rule-based analysis")
            self.enabled = False
    
    def analyze_phishing_content(self, 
                               message_content: str, 
                               extracted_url: Optional[str] = None,
                               enrichment_data: Optional[Dict] = None,
                               url_resolution: Optional[Dict] = None) -> Dict:
        """
        Analyze content for phishing using Gemini AI
        
        Args:
            message_content: The message text to analyze
            extracted_url: URL extracted from the message (if any)
            enrichment_data: Additional data from security services
            url_resolution: URL resolution data for shortened URLs
            
        Returns:
            Dictionary containing AI analysis results
        """
        if not self.enabled:
            return self._fallback_analysis(message_content, extracted_url, enrichment_data)
        
        try:
            # Prepare the prompt for Gemini
            prompt = self._build_analysis_prompt(message_content, extracted_url, enrichment_data, url_resolution)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            print(f"Error during Gemini AI analysis: {str(e)}")
            return self._fallback_analysis(message_content, extracted_url, enrichment_data, url_resolution)
    
    def _build_analysis_prompt(self, 
                              message_content: str, 
                              extracted_url: Optional[str],
                              enrichment_data: Optional[Dict],
                              url_resolution: Optional[Dict] = None) -> str:
        """Build the analysis prompt for Gemini AI"""
        
        prompt = """You are an expert cybersecurity analyst specializing in phishing detection. 
Analyze the provided content and return a JSON response with the following structure:

{
    "is_phishing": boolean,
    "confidence_score": number (0-100),
    "attack_type": "string (PHISHING_LINK, OTP_SCAM, LOTTERY_SCAM, JOB_SCAM, INVESTMENT_SCAM, ROMANCE_SCAM, TECH_SUPPORT_SCAM, MARKETING_LINK, UNKNOWN)",
    "risk_level": "string (LOW, MEDIUM, HIGH, CRITICAL)",
    "indicators": [
        {
            "type": "string",
            "description": "string",
            "severity": "string (LOW, MEDIUM, HIGH)",
            "confidence": number (0-100)
        }
    ],
    "reasoning": "string (detailed explanation)",
    "attacker_intent": "string (explanation of likely attacker goals)",
    "recommended_action": "string (BLOCK, QUARANTINE, VERIFY, CAUTION, ALLOW)"
}

Content to analyze:

Message: """

        if message_content:
            prompt += f"\n\"{message_content}\"\n"
        else:
            prompt += "\n[No message content]\n"
        
        if extracted_url:
            prompt += f"\nURL: {extracted_url}\n"
        
        if enrichment_data:
            prompt += "\nEnrichment Data:\n"
            
            # Include relevant enrichment data
            for key, value in enrichment_data.items():
                if key in ['safe_browsing', 'virustotal', 'urlscan', 'whois', 'tls', 'blacklist_matches']:
                    prompt += f"- {key}: {json.dumps(value, indent=2)}\n"
        
        if url_resolution:
            prompt += "\nURL Resolution Data:\n"
            prompt += f"- Original URL: {url_resolution.get('original_url', 'N/A')}\n"
            prompt += f"- Final URL: {url_resolution.get('final_url', 'N/A')}\n"
            prompt += f"- Final Domain: {url_resolution.get('final_domain', 'N/A')}\n"
            prompt += f"- Is Legitimate Domain: {url_resolution.get('is_legitimate_domain', False)}\n"
            prompt += f"- Page Title: {url_resolution.get('title', 'N/A')}\n"
            prompt += f"- Redirect Count: {len(url_resolution.get('redirect_chain', []))}\n"
            prompt += f"- Is Accessible: {url_resolution.get('is_accessible', False)}\n"
        
        prompt += """

Analysis Guidelines:
1. Consider urgency language, credential requests, financial offers, and suspicious links
2. Evaluate domain reputation, age, and security service verdicts
3. Look for social engineering tactics and emotional manipulation
4. Assess technical indicators like URL structure, TLS certificates, and IP reputation
5. Consider the context and platform where this content appeared
6. IMPORTANT: If a shortened URL resolves to a legitimate marketing domain (like Amazon, Flipkart, etc.) and the message appears to be legitimate marketing content, classify as 'MARKETING_LINK' with low risk
7. Marketing links should have confidence scores between 10-30 and risk level LOW
8. Look for legitimate business purposes: sales, promotions, product launches, newsletters
9. Be thorough but concise in your analysis

Return ONLY the JSON response, no additional text."""

        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse the JSON response from Gemini AI"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Remove any markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            result = json.loads(response_text.strip())
            
            # Validate required fields
            required_fields = ['is_phishing', 'confidence_score', 'attack_type', 'risk_level']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure confidence_score is within bounds
            result['confidence_score'] = max(0, min(100, result.get('confidence_score', 0)))
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing Gemini response: {str(e)}")
            print(f"Raw response: {response_text[:500]}...")
            
            # Return a basic fallback structure
            return {
                "is_phishing": False,
                "confidence_score": 0,
                "attack_type": "UNKNOWN",
                "risk_level": "LOW",
                "indicators": [],
                "reasoning": "Failed to parse AI response",
                "attacker_intent": "Unknown",
                "recommended_action": "VERIFY"
            }
    
    def _fallback_analysis(self, 
                          message_content: str, 
                          extracted_url: Optional[str],
                          enrichment_data: Optional[Dict],
                          url_resolution: Optional[Dict] = None) -> Dict:
        """Fallback analysis when AI is not available"""
        
        # Simple rule-based analysis as fallback
        indicators = []
        confidence_score = 0
        is_phishing = False
        attack_type = "UNKNOWN"
        risk_level = "LOW"
        
        # Check if this might be a legitimate marketing link
        if url_resolution and url_resolution.get('is_legitimate_domain', False):
            attack_type = "MARKETING_LINK"
            confidence_score = 20  # Low confidence for marketing
            risk_level = "LOW"
            indicators.append({
                "type": "LEGITIMATE_MARKETING",
                "description": f"URL resolves to legitimate domain: {url_resolution.get('final_domain', '')}",
                "severity": "LOW",
                "confidence": 80
            })
            
            # Check if message content supports marketing classification
            if message_content:
                content_lower = message_content.lower()
                marketing_keywords = ['sale', 'offer', 'discount', 'shop', 'deal', 'product']
                marketing_matches = sum(1 for keyword in marketing_keywords if keyword in content_lower)
                
                if marketing_matches > 0:
                    indicators.append({
                        "type": "MARKETING_CONTENT",
                        "description": f"Message contains marketing-related keywords",
                        "severity": "LOW",
                        "confidence": 70
                    })
            
            return {
                "is_phishing": False,
                "confidence_score": confidence_score,
                "attack_type": attack_type,
                "risk_level": risk_level,
                "indicators": indicators,
                "reasoning": "URL resolves to legitimate marketing domain with appropriate content",
                "attacker_intent": "Legitimate business marketing/promotion",
                "recommended_action": "ALLOW"
            }
        
        if message_content:
            content_lower = message_content.lower()
            
            # Check for common phishing indicators
            phishing_keywords = {
                'urgent': 15,
                'verify': 20,
                'suspended': 25,
                'click here': 10,
                'act now': 15,
                'limited time': 10,
                'confirm': 15,
                'update': 10,
                'security': 15,
                'account': 15
            }
            
            for keyword, score in phishing_keywords.items():
                if keyword in content_lower:
                    confidence_score += score
                    indicators.append({
                        "type": "SUSPICIOUS_LANGUAGE",
                        "description": f"Contains phishing keyword: '{keyword}'",
                        "severity": "MEDIUM",
                        "confidence": score * 2
                    })
        
        # Check enrichment data for high-confidence signals
        if enrichment_data:
            safe_browsing = enrichment_data.get('safe_browsing', {})
            if safe_browsing.get('verdict') == 'MALICIOUS':
                confidence_score += 60
                is_phishing = True
                attack_type = "PHISHING_LINK"
                risk_level = "HIGH"
                indicators.append({
                    "type": "SECURITY_SERVICE",
                    "description": "Flagged as malicious by Google Safe Browsing",
                    "severity": "HIGH",
                    "confidence": 95
                })
            
            virustotal = enrichment_data.get('virustotal', {})
            malicious_count = virustotal.get('malicious_count', 0)
            if malicious_count > 3:
                confidence_score += 40
                is_phishing = True
                attack_type = "PHISHING_LINK"
                risk_level = "HIGH"
                indicators.append({
                    "type": "SECURITY_SERVICE",
                    "description": f"Flagged by {malicious_count} security engines",
                    "severity": "HIGH",
                    "confidence": 85
                })
        
        # Determine final assessment
        confidence_score = min(100, confidence_score)
        
        if confidence_score >= 70:
            is_phishing = True
            risk_level = "HIGH"
        elif confidence_score >= 40:
            risk_level = "MEDIUM"
        
        # Determine recommended action
        if confidence_score >= 80:
            recommended_action = "BLOCK"
        elif confidence_score >= 60:
            recommended_action = "QUARANTINE"
        elif confidence_score >= 30:
            recommended_action = "VERIFY"
        else:
            recommended_action = "CAUTION"
        
        return {
            "is_phishing": is_phishing,
            "confidence_score": confidence_score,
            "attack_type": attack_type,
            "risk_level": risk_level,
            "indicators": indicators,
            "reasoning": "AI service unavailable, using rule-based fallback analysis",
            "attacker_intent": "Unable to determine without AI analysis",
            "recommended_action": recommended_action
        }
    
    def get_educational_content(self, attack_type: str) -> Dict:
        """Get educational content about specific attack types"""
        
        educational_content = {
            "PHISHING_LINK": {
                "title": "Phishing Link Detection",
                "description": "Malicious links designed to steal credentials or install malware",
                "prevention_tips": [
                    "Hover over links to see the actual destination",
                    "Check for misspelled domains",
                    "Verify requests through official channels",
                    "Look for HTTPS and valid certificates"
                ]
            },
            "OTP_SCAM": {
                "title": "OTP/SMS Scam",
                "description": "Attempts to steal one-time passwords or verification codes",
                "prevention_tips": [
                    "Never share OTP codes with anyone",
                    "Legitimate services won't ask for OTPs via phone/email",
                    "Be suspicious of urgent requests for verification codes",
                    "Use authenticator apps when possible"
                ]
            },
            "LOTTERY_SCAM": {
                "title": "Lottery/Prize Scam",
                "description": "Fraudulent claims of winning prizes to extract money or information",
                "prevention_tips": [
                    "You can't win contests you didn't enter",
                    "Legitimate prizes don't require upfront payments",
                    "Be skeptical of 'limited time' offers",
                    "Verify lottery results through official channels"
                ]
            },
            "JOB_SCAM": {
                "title": "Employment Scam",
                "description": "Fake job offers used for identity theft or advance fee fraud",
                "prevention_tips": [
                    "Research the company thoroughly",
                    "Be wary of jobs requiring upfront payments",
                    "Legitimate employers don't ask for personal financial info upfront",
                    "Meet potential employers in person when possible"
                ]
            },
            "MARKETING_LINK": {
                "title": "Legitimate Marketing Link",
                "description": "Authentic promotional content from legitimate businesses",
                "prevention_tips": [
                    "Even legitimate links should be verified if unexpected",
                    "Check the final destination domain matches the claimed sender",
                    "Be cautious of offers that seem too good to be true",
                    "Verify promotional codes through official channels"
                ]
            }
        }
        
        return educational_content.get(attack_type, {
            "title": "General Security Awareness",
            "description": "Stay vigilant against social engineering attacks",
            "prevention_tips": [
                "Verify requests through official channels",
                "Be suspicious of urgent or threatening messages",
                "Don't click suspicious links or download attachments",
                "Keep software and security tools updated"
            ]
        })

# Global instance
gemini_service = GeminiAIService()
