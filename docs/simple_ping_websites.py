#!/usr/bin/env python3
"""
Simple Website Ping Tool
Uses built-in libraries to test regulatory website connectivity
"""

import urllib.request
import urllib.error
import socket
import time
import json
from datetime import datetime

def ping_website(url, name, timeout=10):
    """Ping a website using built-in urllib"""
    
    try:
        print(f"🔍 Pinging {name} ({url})...")
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'DoganAI-Compliance-Kit/1.0'
            }
        )
        
        start_time = time.time()
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            content = response.read()
            
            result = {
                'name': name,
                'url': url,
                'status_code': response.getcode(),
                'response_time_ms': round(response_time, 2),
                'accessible': True,
                'content_length': len(content),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ {name}: Online ({result['response_time_ms']:.0f}ms)")
            return result
    
    except urllib.error.HTTPError as e:
        print(f"⚠️ {name}: HTTP {e.code}")
        return {
            'name': name,
            'url': url,
            'status_code': e.code,
            'accessible': False,
            'error': f'HTTP {e.code}'
        }
    
    except urllib.error.URLError as e:
        print(f"❌ {name}: Connection failed")
        return {
            'name': name,
            'url': url,
            'accessible': False,
            'error': 'Connection failed'
        }
    
    except socket.timeout:
        print(f"⏰ {name}: Timeout")
        return {
            'name': name,
            'url': url,
            'accessible': False,
            'error': 'Timeout'
        }
    
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return {
            'name': name,
            'url': url,
            'accessible': False,
            'error': str(e)
        }

def main():
    """Test connectivity to regulatory websites"""
    
    print("🌍 Auto-Pinging Saudi Regulatory Websites")
    print("=" * 45)
    
    # Saudi regulatory authority websites
    websites = {
        'NCA': 'https://nca.gov.sa',
        'SAMA': 'https://sama.gov.sa', 
        'MoH': 'https://moh.gov.sa',
        'CITC': 'https://citc.gov.sa',
        'CMA': 'https://cma.org.sa'
    }
    
    results = []
    accessible_count = 0
    
    print(f"Testing {len(websites)} regulatory websites...\n")
    
    for name, url in websites.items():
        result = ping_website(url, name)
        results.append(result)
        
        if result.get('accessible', False):
            accessible_count += 1
        
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"Total: {len(websites)} | Accessible: {accessible_count} | Failed: {len(websites) - accessible_count}")
    print(f"Success Rate: {(accessible_count/len(websites)*100):.1f}%")
    
    # Show accessible sites
    print(f"\n✅ Accessible Sites:")
    for result in results:
        if result.get('accessible', False):
            print(f"   • {result['name']}: {result['response_time_ms']:.0f}ms")
    
    # Show failed sites  
    failed_sites = [r for r in results if not r.get('accessible', False)]
    if failed_sites:
        print(f"\n❌ Failed Sites:")
        for result in failed_sites:
            print(f"   • {result['name']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    output_file = "website_ping_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'scan_time': datetime.now().isoformat(),
            'total_sites': len(websites),
            'accessible_sites': accessible_count,
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    if accessible_count > 0:
        print(f"\n🚀 Next Steps:")
        print("   • Install web scraping tools: pip install requests beautifulsoup4")
        print("   • Run advanced scraper: python regulatory_web_scraper.py") 
        print("   • Extract public compliance data as API fallback")

if __name__ == "__main__":
    main()
