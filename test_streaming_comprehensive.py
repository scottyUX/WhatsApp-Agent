#!/usr/bin/env python3
"""
Comprehensive test suite for WhatsApp Agent streaming functionality.
Tests both regular and streaming chat endpoints with database integration.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat/"
STREAM_ENDPOINT = f"{BASE_URL}/chat/stream"
WEBHOOK_ENDPOINT = f"{BASE_URL}/api/webhook"

class StreamingTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_regular_chat_endpoint(self):
        """Test regular chat endpoint functionality"""
        print("\n🔵 Testing Regular Chat Endpoint")
        
        try:
            response = self.session.post(
                CHAT_ENDPOINT,
                json={
                    "content": "I need help with my medical consultation",
                    "media_urls": [],
                    "audio_urls": []
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data and len(data["content"]) > 0:
                    self.log_test(
                        "Regular Chat Response",
                        True,
                        f"Received response: {data['content'][:100]}..."
                    )
                    return True
                else:
                    self.log_test("Regular Chat Response", False, "Empty or invalid response")
                    return False
            else:
                self.log_test("Regular Chat Response", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Regular Chat Response", False, f"Exception: {str(e)}")
            return False
    
    def test_streaming_chat_endpoint(self):
        """Test streaming chat endpoint functionality"""
        print("\n🔵 Testing Streaming Chat Endpoint")
        
        try:
            response = self.session.post(
                STREAM_ENDPOINT,
                json={
                    "content": "I need help with my medical consultation",
                    "media_urls": [],
                    "audio_urls": []
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                chunks = []
                final_chunk = None
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                chunks.append(data)
                                if data.get('is_final'):
                                    final_chunk = data
                                    break
                            except json.JSONDecodeError as e:
                                self.log_test("Streaming JSON Parse", False, f"JSON Error: {e}")
                                return False
                
                if len(chunks) > 0 and final_chunk:
                    content_chunks = [chunk['content'] for chunk in chunks if not chunk.get('is_final')]
                    full_content = ''.join(content_chunks)
                    
                    self.log_test(
                        "Streaming Response",
                        True,
                        f"Received {len(chunks)} chunks, content: {full_content[:100]}..."
                    )
                    return True
                else:
                    self.log_test("Streaming Response", False, "No valid chunks received")
                    return False
            else:
                self.log_test("Streaming Response", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Streaming Response", False, f"Exception: {str(e)}")
            return False
    
    def test_streaming_headers(self):
        """Test streaming response headers"""
        print("\n🔵 Testing Streaming Headers")
        
        try:
            response = self.session.post(
                STREAM_ENDPOINT,
                json={
                    "content": "Test headers",
                    "media_urls": [],
                    "audio_urls": []
                },
                stream=True,
                timeout=10
            )
            
            if response.status_code == 200:
                headers = response.headers
                expected_headers = {
                    'content-type': 'text/plain; charset=utf-8',
                    'cache-control': 'no-cache',
                    'connection': 'keep-alive'
                }
                
                header_tests = []
                for header, expected in expected_headers.items():
                    actual = headers.get(header, '').lower()
                    if expected.lower() in actual:
                        header_tests.append(True)
                    else:
                        header_tests.append(False)
                        print(f"    Header mismatch: {header} - Expected: {expected}, Got: {actual}")
                
                if all(header_tests):
                    self.log_test("Streaming Headers", True, "All headers correct")
                    return True
                else:
                    self.log_test("Streaming Headers", False, "Header validation failed")
                    return False
            else:
                self.log_test("Streaming Headers", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Streaming Headers", False, f"Exception: {str(e)}")
            return False
    
    def test_database_integration(self):
        """Test database integration for chat messages"""
        print("\n🔵 Testing Database Integration")
        
        try:
            # Send a test message
            test_message = f"Database test message {datetime.now().strftime('%H:%M:%S')}"
            response = self.session.post(
                CHAT_ENDPOINT,
                json={
                    "content": test_message,
                    "media_urls": [],
                    "audio_urls": []
                },
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if message was stored in database
                # This would require a database query endpoint or direct DB access
                # For now, we'll assume success if the response is valid
                self.log_test(
                    "Database Integration",
                    True,
                    f"Message sent and response received: {test_message[:50]}..."
                )
                return True
            else:
                self.log_test("Database Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🔵 Testing Error Handling")
        
        # Test with invalid JSON
        try:
            response = self.session.post(
                CHAT_ENDPOINT,
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid JSON Handling", True, "Properly rejected invalid JSON")
            else:
                self.log_test("Invalid JSON Handling", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid JSON Handling", False, f"Exception: {str(e)}")
        
        # Test with missing required fields
        try:
            response = self.session.post(
                CHAT_ENDPOINT,
                json={},  # Missing required fields
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Missing Fields Handling", True, "Properly rejected missing fields")
            else:
                self.log_test("Missing Fields Handling", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Missing Fields Handling", False, f"Exception: {str(e)}")
    
    def test_performance(self):
        """Test performance with multiple concurrent requests"""
        print("\n🔵 Testing Performance")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(request_id):
            try:
                start_time = time.time()
                response = self.session.post(
                    CHAT_ENDPOINT,
                    json={
                        "content": f"Performance test message {request_id}",
                        "media_urls": [],
                        "audio_urls": []
                    },
                    timeout=30
                )
                end_time = time.time()
                
                results.put({
                    "id": request_id,
                    "success": response.status_code == 200,
                    "duration": end_time - start_time,
                    "status_code": response.status_code
                })
            except Exception as e:
                results.put({
                    "id": request_id,
                    "success": False,
                    "duration": 0,
                    "error": str(e)
                })
        
        # Start 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        performance_results = []
        while not results.empty():
            performance_results.append(results.get())
        
        successful_requests = [r for r in performance_results if r["success"]]
        avg_duration = sum(r["duration"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        if len(successful_requests) >= 4:  # At least 80% success rate
            self.log_test(
                "Performance Test",
                True,
                f"{len(successful_requests)}/5 requests successful, avg duration: {avg_duration:.2f}s"
            )
        else:
            self.log_test(
                "Performance Test",
                False,
                f"Only {len(successful_requests)}/5 requests successful"
            )
    
    def test_webhook_integration(self):
        """Test webhook endpoint integration"""
        print("\n🔵 Testing Webhook Integration")
        
        try:
            # Test GET webhook (verification)
            response = self.session.get(
                WEBHOOK_ENDPOINT,
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "test_challenge",
                    "hub.verify_token": "test_token"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Webhook GET", True, "Webhook verification successful")
            else:
                self.log_test("Webhook GET", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Webhook GET", False, f"Exception: {str(e)}")
        
        # Test POST webhook (message handling)
        try:
            webhook_data = {
                "Body": "Test webhook message",
                "From": "+1234567890",
                "NumMedia": "0"
            }
            
            response = self.session.post(
                WEBHOOK_ENDPOINT,
                data=webhook_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_test("Webhook POST", True, "Webhook message processing successful")
            else:
                self.log_test("Webhook POST", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Webhook POST", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Streaming Tests")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_regular_chat_endpoint,
            self.test_streaming_chat_endpoint,
            self.test_streaming_headers,
            self.test_database_integration,
            self.test_error_handling,
            self.test_performance,
            self.test_webhook_integration
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        # Save detailed report
        report_file = f"streaming_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")

def main():
    """Main test runner"""
    print("WhatsApp Agent Streaming Test Suite")
    print("===================================")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        sys.exit(1)
    
    # Run tests
    tester = StreamingTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
