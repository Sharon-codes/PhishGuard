"""
URL Resolution Service for PhishGuard
Resolves shortened URLs and analyzes final destinations
"""

import requests
import urllib.parse
from urllib.parse import urlparse
import time
from typing import Dict, Optional, Tuple

class URLResolver:
    """Service for resolving shortened URLs and analyzing destinations"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Common URL shorteners
        self.shorteners = [
            'bit.ly', 't.co', 'tinyurl.com', 'ow.ly', 'buff.ly', 
            'shorturl.at', 'is.gd', 'goo.gl', 'rb.gy', 'tiny.cc',
            'shorte.st', 'adf.ly', 'linktr.ee', 'cutt.ly', 'short.link'
        ]
        
        # Known legitimate marketing domains (including country-specific versions)
        self.legitimate_marketing_domains = [
            'amazon.com', 'amazon.in', 'amazon.co.uk', 'amazon.de', 'amazon.fr',
            'flipkart.com', 'myntra.com', 'ajio.com', 'nykaa.com', 
            'shopify.com', 'bigbasket.com', 'grofers.com', 'blinkit.com',
            'swiggy.com', 'zomato.com', 'bookmyshow.com', 'makemytrip.com',
            'goibibo.com', 'paytm.com', 'phonepe.com', 'googlepay.com',
            'youtube.com', 'youtu.be', 'netflix.com', 'hotstar.com', 'primevideo.com',
            'spotify.com', 'gaana.com', 'jiosaavn.com', 'airtel.com',
            'jio.com', 'vodafone.com', 'idea.com', 'bsnl.in',
            'linkedin.com', 'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
            'whatsapp.com', 'telegram.org', 'discord.com', 'zoom.us',
            'microsoft.com', 'google.com', 'apple.com', 'samsung.com',
            'oneplus.com', 'xiaomi.com', 'realme.com', 'oppo.com',
            'vivo.com', 'nokia.com', 'sony.com', 'lg.com', 'mi.com',
            'ebay.com', 'ebay.in', 'alibaba.com', 'aliexpress.com',
            'walmart.com', 'target.com', 'bestbuy.com', 'tesco.com'
        ]
    
    def is_shortened_url(self, url: str) -> bool:
        """Check if URL uses a known shortener service"""
        try:
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'http://{url}')
            domain = parsed.hostname or ''
            return any(shortener in domain.lower() for shortener in self.shorteners)
        except:
            return False
    
    def resolve_url(self, url: str, timeout: int = 10, max_redirects: int = 5) -> Dict:
        """
        Resolve a URL and get information about the final destination
        
        Args:
            url: The URL to resolve
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
            
        Returns:
            Dictionary with resolution information
        """
        result = {
            'original_url': url,
            'final_url': None,
            'redirect_chain': [],
            'status_code': None,
            'error': None,
            'is_accessible': False,
            'response_time': None,
            'content_type': None,
            'title': None,
            'final_domain': None,
            'is_legitimate_domain': False
        }
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f'http://{url}'
            
            start_time = time.time()
            
            # Follow redirects manually to track the chain
            current_url = url
            redirect_count = 0
            
            while redirect_count < max_redirects:
                try:
                    response = self.session.head(
                        current_url, 
                        timeout=timeout, 
                        allow_redirects=False
                    )
                    
                    result['redirect_chain'].append({
                        'url': current_url,
                        'status_code': response.status_code
                    })
                    
                    # If no redirect, this is the final URL
                    if response.status_code not in [301, 302, 303, 307, 308]:
                        result['final_url'] = current_url
                        result['status_code'] = response.status_code
                        result['is_accessible'] = 200 <= response.status_code < 400
                        break
                    
                    # Get redirect location
                    location = response.headers.get('location', '')
                    if not location:
                        break
                    
                    # Handle relative URLs
                    if location.startswith('/'):
                        parsed_current = urlparse(current_url)
                        location = f"{parsed_current.scheme}://{parsed_current.netloc}{location}"
                    elif not location.startswith(('http://', 'https://')):
                        parsed_current = urlparse(current_url)
                        location = f"{parsed_current.scheme}://{parsed_current.netloc}/{location}"
                    
                    current_url = location
                    redirect_count += 1
                    
                except requests.exceptions.RequestException as e:
                    result['error'] = f"Request failed: {str(e)}"
                    break
            
            # If we hit max redirects, current_url is the final URL
            if redirect_count >= max_redirects:
                result['final_url'] = current_url
                result['error'] = "Maximum redirects exceeded"
            
            result['response_time'] = time.time() - start_time
            
            # Try to get more information about the final URL
            if result['final_url'] and result.get('is_accessible', False):
                try:
                    # Get the actual page content (first 1KB) to extract title
                    page_response = self.session.get(
                        result['final_url'], 
                        timeout=timeout,
                        stream=True
                    )
                    
                    result['content_type'] = page_response.headers.get('content-type', '')
                    
                    # Read first 1KB to extract title
                    content_chunk = b''
                    for chunk in page_response.iter_content(chunk_size=1024):
                        content_chunk += chunk
                        if len(content_chunk) >= 1024:
                            break
                    
                    # Extract title if it's HTML content
                    if 'text/html' in result['content_type']:
                        content_str = content_chunk.decode('utf-8', errors='ignore')
                        title_start = content_str.find('<title>')
                        title_end = content_str.find('</title>')
                        if title_start != -1 and title_end != -1:
                            result['title'] = content_str[title_start + 7:title_end].strip()
                    
                except:
                    pass  # Don't fail if we can't get page content
            
            # Analyze final domain
            if result['final_url']:
                try:
                    parsed_final = urlparse(result['final_url'])
                    result['final_domain'] = parsed_final.hostname or ''
                    
                    # Check if final domain is in our legitimate list
                    domain_lower = result['final_domain'].lower()
                    result['is_legitimate_domain'] = any(
                        domain_lower == legit_domain or domain_lower.endswith('.' + legit_domain)
                        for legit_domain in self.legitimate_marketing_domains
                    )
                    print(f"[URL Resolution] Final domain: {domain_lower}, Is legitimate: {result['is_legitimate_domain']}")
                    
                except:
                    pass
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_marketing_legitimacy(self, resolution_result: Dict, content_text: str = "") -> Dict:
        """
        Analyze if a resolved URL appears to be a legitimate marketing link
        
        Args:
            resolution_result: Result from resolve_url()
            content_text: Associated message text
            
        Returns:
            Dictionary with marketing analysis
        """
        analysis = {
            'is_likely_marketing': False,
            'confidence': 0,
            'indicators': [],
            'risk_factors': []
        }
        
        # Check if resolution was successful
        if not resolution_result.get('is_accessible', False):
            analysis['risk_factors'].append('URL is not accessible')
            return analysis
        
        # Check if final domain is legitimate
        if resolution_result.get('is_legitimate_domain', False):
            analysis['confidence'] += 40
            analysis['indicators'].append('Resolves to known legitimate domain')
            print(f"[Marketing Analysis] Legitimate domain detected: {resolution_result.get('final_domain', '')}")
            print(f"[Marketing Analysis] Current confidence: {analysis['confidence']}")
        
        # Check title for marketing indicators
        title = resolution_result.get('title', '').lower()
        if title:
            marketing_keywords = [
                'sale', 'offer', 'discount', 'deal', 'shop', 'buy',
                'product', 'store', 'mall', 'mart', 'shopping',
                'order', 'cart', 'checkout', 'payment', 'official'
            ]
            
            title_marketing_count = sum(1 for keyword in marketing_keywords if keyword in title)
            if title_marketing_count >= 2:
                analysis['confidence'] += 20
                analysis['indicators'].append(f'Title contains marketing keywords: {title[:50]}')
        
        # Check URL structure
        final_url = resolution_result.get('final_url', '').lower()
        if final_url:
            # Look for marketing URL patterns
            marketing_paths = [
                '/product/', '/item/', '/deal/', '/offer/', '/sale/',
                '/shop/', '/store/', '/campaign/', '/promo/', '/landing/'
            ]
            
            url_marketing_indicators = sum(1 for path in marketing_paths if path in final_url)
            if url_marketing_indicators > 0:
                analysis['confidence'] += 15
                analysis['indicators'].append('URL contains marketing path indicators')
        
        # Check message content for marketing context
        content_lower = content_text.lower()
        if content_lower:
            # Legitimate marketing phrases
            legit_marketing_phrases = [
                'exclusive offer', 'limited time', 'shop now', 'official store',
                'free shipping', 'cashback', 'rewards', 'membership',
                'subscribe', 'newsletter', 'brand new', 'latest collection'
            ]
            
            legit_count = sum(1 for phrase in legit_marketing_phrases if phrase in content_lower)
            if legit_count > 0:
                analysis['confidence'] += 10
                analysis['indicators'].append('Message contains legitimate marketing language')
            
            # Suspicious phrases that might indicate phishing even in marketing context
            suspicious_phrases = [
                'urgent action', 'account suspended', 'verify immediately',
                'click now or lose', 'limited spots', 'act fast',
                'share otp', 'enter password', 'confirm details'
            ]
            
            suspicious_count = sum(1 for phrase in suspicious_phrases if phrase in content_lower)
            if suspicious_count > 0:
                analysis['confidence'] -= 20
                analysis['risk_factors'].append('Contains suspicious urgency language')
        
        # Check redirect chain length
        redirect_count = len(resolution_result.get('redirect_chain', []))
        if redirect_count > 3:
            analysis['confidence'] -= 10
            analysis['risk_factors'].append(f'Long redirect chain ({redirect_count} hops)')
        
        # Final assessment
        analysis['confidence'] = max(0, min(100, analysis['confidence']))
        analysis['is_likely_marketing'] = analysis['confidence'] >= 40  # Lower threshold for marketing detection
        
        return analysis

# Global instance
url_resolver = URLResolver()
