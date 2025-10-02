"""
Test script for the streaming chat endpoint.
Tests the POST /chat/stream endpoint with Server-Sent Events.
"""

import json
import httpx
import asyncio


class StreamingChatTester:
    """Test class for streaming chat endpoint."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/chat/stream"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
        }
    
    async def test_streaming_response(self, payload: dict, test_name: str):
        """Test streaming response from the chat endpoint."""
        print(f"\n🧪 {test_name}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    self.endpoint,
                    json=payload,
                    headers=self.headers
                ) as response:
                    
                    print(f"   Status Code: {response.status_code}")
                    
                    if response.status_code != 200:
                        content = await response.aread()
                        print(f"   Error Response: {content.decode()}")
                        return False
                    
                    print("   Streaming Response:")
                    chunk_count = 0
                    full_content = ""
                    
                    async for chunk in response.aiter_text():
                        if chunk.strip():
                            chunk_count += 1
                            try:
                                # Parse SSE format
                                if chunk.startswith("data: "):
                                    data_str = chunk[6:].strip()
                                    if data_str:
                                        data = json.loads(data_str)
                                        content = data.get('content', '')
                                        is_final = data.get('is_final', False)
                                        timestamp = data.get('timestamp', '')
                                        
                                        if content:
                                            print(f"     Chunk {chunk_count}: '{content}'")
                                            full_content += content
                                        
                                        if is_final:
                                            print(f"     ✅ Stream completed at {timestamp}")
                                            break
                                            
                            except json.JSONDecodeError as e:
                                print(f"     ⚠️ Invalid JSON in chunk {chunk_count}: {chunk}")
                    
                    print(f"   📝 Full Response: '{full_content}'")
                    print(f"   📊 Total chunks received: {chunk_count}")
                    return True
                    
        except httpx.ConnectError:
            print(f"   ❌ Connection failed. Is the server running on {self.base_url}?")
            return False
        except httpx.TimeoutError:
            print("   ❌ Request timed out")
            return False
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return False
    
    async def test_basic_streaming(self):
        """Test basic streaming functionality."""
        payload = {
            "content": "Guten Abend",
            "media_urls": None,
            "audio_urls": None
        }
        return await self.test_streaming_response(payload, "Basic Streaming Test")
    
    
    async def test_streaming_complex_query(self):
        """Test streaming with a complex query."""
        payload = {
            "content": "I'm interested in hair transplant procedures. Can you explain the different types available, the recovery process, and what I should expect during consultation?",
            "media_urls": None,
            "audio_urls": None
        }
        return await self.test_streaming_response(payload, "Complex Query Streaming Test")
    
    async def run_all_tests(self):
        """Run all streaming tests."""
        print("=" * 60)
        print("🌊 STREAMING CHAT API TESTS")
        print(f"🎯 Target: {self.base_url}")
        print("=" * 60)
        
        
        tests = [
            ("Basic Streaming", self.test_basic_streaming),
            # ("Complex Query Streaming", self.test_streaming_complex_query),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 Running: {test_name}")
                if await test_func():
                    passed += 1
                    print(f"   ✅ {test_name} completed successfully")
                else:
                    print(f"   ❌ {test_name} failed")
                    
                # Small delay between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Test '{test_name}' encountered an error: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 STREAMING RESULTS: {passed}/{total} tests completed successfully")
        print("=" * 60)
        
        if passed == total:
            print("🎉 All streaming tests completed successfully!")
        else:
            print(f"⚠️ {total - passed} test(s) had issues")


async def main():
    """Main function to run the streaming tests."""
    base_url = "http://localhost:8080"
    tester = StreamingChatTester(base_url=base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    # Run the streaming tests
    asyncio.run(main())