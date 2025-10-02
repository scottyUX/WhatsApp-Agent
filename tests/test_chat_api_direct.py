"""
Direct HTTP test script for the chat router endpoint.
Tests the POST /chat/ endpoint by sending real HTTP requests to a running server.
No TestClient or app imports - pure HTTP requests.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
import httpx


class DirectChatAPITester:
    """Test class that sends direct HTTP requests to the chat API."""
    
    def __init__(self, base_url: str = "https://whats-app-agent-sandbox.vercel.app"):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/chat/"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def send_request(self, payload: Dict[str, Any]) -> Optional[httpx.Response]:
        """Send a POST request to the chat endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers=self.headers
                )
                return response
            except httpx.ConnectError:
                print(f"❌ Connection failed. Is the server running on {self.base_url}?")
                return None
            except httpx.TimeoutError:
                print("❌ Request timed out")
                return None
            except Exception as e:
                print(f"❌ Request failed: {e}")
                return None
    
    async def test_basic_text_message(self) -> bool:
        """Test basic text message functionality."""
        print("🧪 Testing basic text message...")
        
        payload = {
            "content": "Guten Abend",
            "media_urls": None,
            "audio_urls": None
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200 and "content" in response_data:
                print("   ✅ Basic text message test passed!")
                return True
            else:
                print("   ❌ Basic text message test failed!")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_message_with_media(self) -> bool:
        """Test message with media URLs."""
        print("\n🧪 Testing message with media URLs...")
        
        payload = {
            "content": "Check out these images!",
            "media_urls": [
                "https://picsum.photos/200/300",
                "https://picsum.photos/400/600"
            ],
            "audio_urls": None
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Media URLs test passed!")
                return True
            else:
                print("   ❌ Media URLs test failed!")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_message_with_audio(self) -> bool:
        """Test message with audio URLs."""
        print("\n🧪 Testing message with audio URLs...")
        
        payload = {
            "content": "Listen to this audio",
            "media_urls": None,
            "audio_urls": [
                "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
                "https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav"
            ]
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Audio URLs test passed!")
                return True
            else:
                print("   ❌ Audio URLs test failed!")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_complete_message(self) -> bool:
        """Test message with all fields populated."""
        print("\n🧪 Testing complete message with all fields...")
        
        payload = {
            "content": "Here's a complete multimedia message!",
            "media_urls": ["https://picsum.photos/300/400"],
            "audio_urls": ["https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"]
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Complete message test passed!")
                return True
            else:
                print("   ❌ Complete message test failed!")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_empty_message(self) -> bool:
        """Test empty message handling."""
        print("\n🧪 Testing empty message...")
        
        payload = {
            "content": None,
            "media_urls": None,
            "audio_urls": None
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            print("   ✅ Empty message test completed!")
            return True
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_minimal_payload(self) -> bool:
        """Test with minimal payload (only content)."""
        print("\n🧪 Testing minimal payload...")
        
        payload = {
            "content": "Just a simple message"
        }
        
        response = await self.send_request(payload)
        if response is None:
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                print("   ✅ Minimal payload test passed!")
                return True
            else:
                print("   ❌ Minimal payload test failed!")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text}")
            return False
    
    async def test_invalid_payloads(self) -> bool:
        """Test various invalid payload scenarios."""
        print("\n🧪 Testing invalid payloads...")
        
        invalid_payloads = [
            {"invalid_field": "should not work"},
            {"content": 12345},  # Wrong type
            {},  # Empty object
            {"content": "", "media_urls": "not_a_list"},  # Wrong type for media_urls
        ]
        
        all_handled = True
        
        for i, payload in enumerate(invalid_payloads, 1):
            print(f"   Testing invalid payload {i}: {payload}")
            
            response = await self.send_request(payload)
            if response is None:
                continue
            
            print(f"   Status Code: {response.status_code}")
            
            # We expect either 422 (validation error) or 400 (bad request)
            if response.status_code in [400, 422]:
                print(f"   ✅ Invalid payload {i} properly rejected")
            else:
                print(f"   ⚠️ Invalid payload {i} got unexpected status: {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response text: {response.text}")
        
        return True
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting by sending multiple rapid requests."""
        print("\n🧪 Testing rate limiting...")
        
        payload = {
            "content": "Rate limit test message",
            "media_urls": None,
            "audio_urls": None
        }
        
        # Send 15 requests rapidly
        tasks = []
        for i in range(15):
            tasks.append(self.send_request(payload))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        status_codes = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"   Request {i+1}: Exception - {response}")
            elif response is not None:
                status_codes.append(response.status_code)
                print(f"   Request {i+1}: {response.status_code}")
            else:
                print(f"   Request {i+1}: Failed")
        
        # Check if any requests were rate limited (429)
        if 429 in status_codes:
            print("   ✅ Rate limiting is working!")
        else:
            print("   ⚠️ No rate limiting detected (this might be expected)")
        
        return True

    async def run_all_tests(self) -> None:
        """Run all tests in sequence."""
        print("=" * 60)
        print("🚀 DIRECT HTTP CHAT API TESTS")
        print(f"🎯 Target: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Basic Text Message", self.test_basic_text_message),
            # ("Message with Media", self.test_message_with_media),
            # ("Message with Audio", self.test_message_with_audio),
            # ("Complete Message", self.test_complete_message),
            # ("Empty Message", self.test_empty_message),
            # ("Minimal Payload", self.test_minimal_payload),
            # ("Invalid Payloads", self.test_invalid_payloads),
            # ("Rate Limiting", self.test_rate_limiting),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if await test_func():
                    passed += 1
                    
                # Small delay between tests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Test '{test_name}' encountered an error: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 RESULTS: {passed}/{total} tests passed")
        print("=" * 60)
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️ {total - passed} test(s) failed or had issues")


async def main():
    """Main function to run the tests."""
    base_url = "http://localhost:8080"
    tester = DirectChatAPITester(base_url=base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())