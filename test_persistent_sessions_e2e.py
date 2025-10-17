#!/usr/bin/env python3
"""
End-to-End Test for Persistent Session Storage

This script tests the complete flow of persistent session management
to ensure conversations don't reset between messages.
"""

import asyncio
import uuid
import time
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


class PersistentSessionTester:
    """End-to-end tester for persistent session storage."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
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
    
    def generate_device_id(self) -> str:
        """Generate a unique device ID for testing."""
        return f"test-device-{uuid.uuid4().hex[:8]}"
    
    def send_chat_message(self, device_id: str, message: str) -> Optional[Dict]:
        """Send a chat message and return the response."""
        try:
            url = f"{self.base_url}/chat/stream"
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "X-Device-ID": device_id
            }
            data = {
                "content": message,
                "media_urls": [],
                "audio_urls": []
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                # Parse streaming response
                content = response.text
                # Extract the actual message content (simplified parsing)
                if "data:" in content:
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if data.get('content') and not data.get('is_final'):
                                    return {"content": data['content'], "status": "success"}
                            except json.JSONDecodeError:
                                continue
                
                # Fallback: return raw content
                return {"content": content, "status": "success"}
            else:
                return {"content": f"HTTP {response.status_code}", "status": "error"}
                
        except Exception as e:
            return {"content": str(e), "status": "error"}
    
    def test_basic_connectivity(self) -> bool:
        """Test basic connectivity to the backend."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            self.log_test(
                "Basic Connectivity", 
                success, 
                f"Status: {response.status_code}"
            )
            return success
        except Exception as e:
            self.log_test("Basic Connectivity", False, str(e))
            return False
    
    def test_single_device_conversation(self) -> bool:
        """Test that a single device maintains conversation context."""
        device_id = self.generate_device_id()
        
        # First message
        response1 = self.send_chat_message(device_id, "Hello, I want to schedule an appointment")
        if response1["status"] != "success":
            self.log_test("Single Device - First Message", False, response1["content"])
            return False
        
        # Check for reset message
        has_reset = "I've reset our conversation" in response1["content"]
        self.log_test("Single Device - First Message", True, f"Reset detected: {has_reset}")
        
        # Wait a moment
        time.sleep(2)
        
        # Second message - should maintain context
        response2 = self.send_chat_message(device_id, "What are your available times?")
        if response2["status"] != "success":
            self.log_test("Single Device - Second Message", False, response2["content"])
            return False
        
        # Check for reset message in second response
        has_reset_second = "I've reset our conversation" in response2["content"]
        success = not has_reset_second
        
        self.log_test(
            "Single Device - Context Persistence", 
            success, 
            f"Second message reset: {has_reset_second}"
        )
        
        return success
    
    def test_multiple_devices_isolation(self) -> bool:
        """Test that different devices have isolated conversations."""
        device1 = self.generate_device_id()
        device2 = self.generate_device_id()
        
        # Device 1 starts conversation
        response1 = self.send_chat_message(device1, "Hello, I want to schedule an appointment")
        if response1["status"] != "success":
            self.log_test("Multi Device - Device 1", False, response1["content"])
            return False
        
        # Device 2 starts different conversation
        response2 = self.send_chat_message(device2, "I need help with hair transplant")
        if response2["status"] != "success":
            self.log_test("Multi Device - Device 2", False, response2["content"])
            return False
        
        # Device 1 continues - should not be affected by device 2
        response1_continue = self.send_chat_message(device1, "What are your prices?")
        if response1_continue["status"] != "success":
            self.log_test("Multi Device - Device 1 Continue", False, response1_continue["content"])
            return False
        
        # Check that device 1 didn't get reset by device 2's conversation
        has_reset = "I've reset our conversation" in response1_continue["content"]
        success = not has_reset
        
        self.log_test(
            "Multi Device - Isolation", 
            success, 
            f"Device 1 reset by Device 2: {has_reset}"
        )
        
        return success
    
    def test_session_persistence_across_requests(self) -> bool:
        """Test that sessions persist across multiple requests."""
        device_id = self.generate_device_id()
        
        # Send multiple messages with delays
        messages = [
            "Hello, I want to schedule an appointment",
            "I'm interested in hair transplant",
            "What are your prices?",
            "When can I book?",
            "Thank you for the information"
        ]
        
        reset_count = 0
        total_messages = len(messages)
        
        for i, message in enumerate(messages):
            response = self.send_chat_message(device_id, message)
            if response["status"] != "success":
                self.log_test(f"Persistence - Message {i+1}", False, response["content"])
                return False
            
            has_reset = "I've reset our conversation" in response["content"]
            if has_reset:
                reset_count += 1
            
            # Small delay between messages
            time.sleep(1)
        
        success = reset_count == 0  # Should have no resets
        self.log_test(
            "Session Persistence", 
            success, 
            f"Resets: {reset_count}/{total_messages}"
        )
        
        return success
    
    def test_debug_text_removal(self) -> bool:
        """Test that debug text is not visible in UI responses."""
        device_id = self.generate_device_id()
        
        response = self.send_chat_message(device_id, "Hello")
        if response["status"] != "success":
            self.log_test("Debug Text Removal", False, response["content"])
            return False
        
        # Check for debug text that should not be visible
        has_debug_text = "🟦 SCHEDULING AGENT" in response["content"]
        success = not has_debug_text
        
        self.log_test(
            "Debug Text Removal", 
            success, 
            f"Debug text visible: {has_debug_text}"
        )
        
        return success
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid requests."""
        # Test with missing device ID
        try:
            url = f"{self.base_url}/chat/stream"
            headers = {"Content-Type": "application/json"}
            data = {"content": "Hello", "media_urls": [], "audio_urls": []}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            # Should still work with default device ID
            success = response.status_code == 200
            self.log_test("Error Handling - Missing Device ID", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Error Handling - Missing Device ID", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all E2E tests."""
        print("🧪 Starting End-to-End Tests for Persistent Session Storage")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run tests
        tests = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Single Device Conversation", self.test_single_device_conversation),
            ("Multiple Devices Isolation", self.test_multiple_devices_isolation),
            ("Session Persistence", self.test_session_persistence_across_requests),
            ("Debug Text Removal", self.test_debug_text_removal),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} passed")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if passed == total:
            print("🎉 All tests passed! Persistent session storage is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return {
            "passed": passed,
            "total": total,
            "duration": duration,
            "results": self.test_results
        }


async def main():
    """Main test runner."""
    # Configuration
    BASE_URL = "https://whats-app-agent-git-feat-scheduling-agent-d-39828d-whatsapp-bot.vercel.app"
    
    print("🚀 Persistent Session Storage E2E Test")
    print(f"🌐 Testing against: {BASE_URL}")
    print()
    
    # Run tests
    tester = PersistentSessionTester(BASE_URL)
    results = tester.run_all_tests()
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: test_results.json")
    
    return results["passed"] == results["total"]


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)



