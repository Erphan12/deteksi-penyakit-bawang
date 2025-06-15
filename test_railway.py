#!/usr/bin/env python3
"""
Script untuk testing Railway deployment
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

def test_railway_deployment(base_url):
    """Test Railway deployment endpoints"""
    
    print(f"🚂 Testing Railway Deployment: {base_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        {
            'name': 'Homepage',
            'url': '/',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'API Info',
            'url': '/api',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Health Check',
            'url': '/api/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Disease Info',
            'url': '/api/diseases',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'History',
            'url': '/api/history',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Stats',
            'url': '/api/stats',
            'method': 'GET',
            'expected_status': 200
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Testing {endpoint['name']}...")
            
            url = urljoin(base_url, endpoint['url'])
            start_time = time.time()
            
            response = requests.get(url, timeout=30)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            status = "✅ PASS" if response.status_code == endpoint['expected_status'] else "❌ FAIL"
            
            result = {
                'name': endpoint['name'],
                'url': url,
                'status_code': response.status_code,
                'expected_status': endpoint['expected_status'],
                'response_time': response_time,
                'status': status,
                'content_length': len(response.content)
            }
            
            results.append(result)
            
            print(f"   {status} - {response.status_code} - {response_time}ms")
            
            # Show response preview for API endpoints
            if endpoint['url'].startswith('/api') and response.status_code == 200:
                try:
                    data = response.json()
                    if 'message' in data:
                        print(f"   📝 Message: {data['message']}")
                    if 'version' in data:
                        print(f"   🏷️ Version: {data['version']}")
                except:
                    pass
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Request took longer than 30 seconds")
            results.append({
                'name': endpoint['name'],
                'url': url,
                'status': '⏰ TIMEOUT',
                'error': 'Request timeout'
            })
            
        except requests.exceptions.ConnectionError:
            print(f"   🔌 CONNECTION ERROR - Cannot connect to server")
            results.append({
                'name': endpoint['name'],
                'url': url,
                'status': '🔌 CONNECTION ERROR',
                'error': 'Connection failed'
            })
            
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            results.append({
                'name': endpoint['name'],
                'url': url,
                'status': '❌ ERROR',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.get('status') == '✅ PASS')
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Railway deployment is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the details above.")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        print(f"  {result['status']} {result['name']}")
        if 'response_time' in result:
            print(f"     Response Time: {result['response_time']}ms")
        if 'error' in result:
            print(f"     Error: {result['error']}")
    
    return results

def test_file_upload(base_url):
    """Test file upload functionality"""
    print("\n🖼️ Testing File Upload...")
    
    try:
        # Create a simple test image (1x1 pixel PNG)
        import io
        from PIL import Image
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        url = urljoin(base_url, '/api/detect')
        files = {'image': ('test.png', img_bytes, 'image/png')}
        
        print("📤 Uploading test image...")
        response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"   Disease: {data.get('disease', 'N/A')}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}%")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except ImportError:
        print("⚠️ Pillow not available, skipping upload test")
    except Exception as e:
        print(f"❌ Upload test error: {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_railway.py <railway_url>")
        print("Example: python test_railway.py https://your-app.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Ensure URL ends with /
    if not base_url.endswith('/'):
        base_url += '/'
    
    # Test basic endpoints
    results = test_railway_deployment(base_url)
    
    # Test file upload if basic tests pass
    api_working = any(r.get('name') == 'API Info' and r.get('status') == '✅ PASS' for r in results)
    if api_working:
        test_file_upload(base_url)
    
    print("\n🔗 Quick Links:")
    print(f"   🌐 App: {base_url}")
    print(f"   🔧 API: {base_url}api")
    print(f"   ❤️ Health: {base_url}api/health")

if __name__ == "__main__":
    main()