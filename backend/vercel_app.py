"""
Vercel-compatible entry point for PhishGuard backend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint"""
    return jsonify({
        "service": "PhishGuard API",
        "status": "running",
        "ai_enabled": False,
        "ai_service": "Debug Mode",
        "version": "2.0.0-debug"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Simple analysis endpoint for debugging"""
    try:
        data = request.get_json()
        if not data or 'raw_input' not in data:
            return jsonify({"error": "No raw_input provided"}), 400
        
        raw_input = data.get('raw_input', '')
        
        # Simple response for debugging
        return jsonify({
            "final_score": 25,
            "heuristic_score": 25,
            "llm_score": 25,
            "ai_score": 25,
            "risk_level": "LOW",
            "action": "SAFE_TO_CLICK_AFTER_CHECKS",
            "confidence_pct": 50,
            "attack_type": "UNKNOWN",
            "extracted_url": raw_input if raw_input.startswith('http') else None,
            "multiple_urls": False,
            "top_reasons": [{
                "reason": "Debug mode - simplified analysis",
                "evidence": raw_input[:100],
                "source": "debug",
                "weight": 25
            }],
            "provenance": [],
            "attacker_intent_explanation": "Debug mode - no AI analysis available",
            "ai_reasoning": "Running in debug mode for serverless testing",
            "is_ai_powered": False,
            "url_resolution": None,
            "marketing_analysis": None,
            "suggested_action_text": "Debug mode - exercise normal caution when accessing this content.",
            "marketing_notice": None,
            "automation_advice": {
                "can_automate": False,
                "recommended_actions": []
            },
            "education_tip": "Debug mode active - AI features disabled for testing.",
            "note": "Debug mode - simplified analysis for serverless testing"
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# Export for Vercel
application = app
