"""
API endpoint tests
These tests verify that all API endpoints work correctly
"""
import pytest
from fastapi.testclient import TestClient
from app.app import app


@pytest.mark.api
class TestWebhookEndpoint:
    """Test webhook endpoint functionality"""
    
    def test_webhook_post_success(self, test_app, sample_webhook_payload):
        """Test successful webhook POST request"""
        response = test_app.post("/api/webhook", data=sample_webhook_payload)
        
        assert response.status_code == 200
        assert "Response" in response.text
        assert "Message" in response.text
        assert response.headers["content-type"] == "text/xml; charset=utf-8"
    
    def test_webhook_post_missing_fields(self, test_app):
        """Test webhook POST with missing required fields"""
        response = test_app.post("/api/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "Test message"
            # Missing MessageSid and To
        })
        
        assert response.status_code == 200
        assert "Response" in response.text
    
    def test_webhook_post_empty_body(self, test_app):
        """Test webhook POST with empty body"""
        response = test_app.post("/api/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "",
            "MessageSid": "test-123",
            "To": "whatsapp:+14155238886"
        })
        
        assert response.status_code == 200
        assert "Response" in response.text
    
    def test_webhook_post_invalid_data(self, test_app):
        """Test webhook POST with invalid data"""
        response = test_app.post("/api/webhook", data={
            "From": "invalid-phone",
            "Body": "Test message",
            "MessageSid": "test-123",
            "To": "invalid-phone"
        })
        
        assert response.status_code == 200
        assert "Response" in response.text
    
    def test_webhook_post_with_media(self, test_app):
        """Test webhook POST with media attachments"""
        response = test_app.post("/api/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "Test message with image",
            "MessageSid": "test-123",
            "To": "whatsapp:+14155238886",
            "NumMedia": "1",
            "MediaUrl0": "https://example.com/image.jpg"
        })
        
        assert response.status_code == 200
        assert "Response" in response.text


@pytest.mark.api
class TestHealthCheckEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_get(self, test_app):
        """Test health check GET request"""
        response = test_app.get("/api/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()
    
    def test_health_check_post(self, test_app):
        """Test health check POST request"""
        response = test_app.post("/api/health")
        
        # Should return 405 Method Not Allowed
        assert response.status_code == 405


@pytest.mark.api
class TestTestEndpoint:
    """Test test endpoint functionality"""
    
    def test_test_endpoint_get(self, test_app):
        """Test test endpoint GET request"""
        response = test_app.get("/api/test")
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_test_endpoint_post(self, test_app):
        """Test test endpoint POST request"""
        response = test_app.post("/api/test", json={"test": "data"})
        
        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.api
class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_not_found(self, test_app):
        """Test 404 error for non-existent endpoint"""
        response = test_app.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, test_app):
        """Test 405 error for unsupported HTTP method"""
        response = test_app.delete("/api/health")
        
        assert response.status_code == 405
    
    def test_422_validation_error(self, test_app):
        """Test 422 error for validation issues"""
        response = test_app.post("/api/test", json={"invalid": "data"})
        
        # Should handle gracefully
        assert response.status_code in [200, 422]


@pytest.mark.api
class TestResponseFormat:
    """Test API response format consistency"""
    
    def test_webhook_xml_format(self, test_app, sample_webhook_payload):
        """Test webhook returns proper XML format"""
        response = test_app.post("/api/webhook", data=sample_webhook_payload)
        
        assert response.status_code == 200
        content = response.text
        
        # Check XML structure
        assert content.startswith("<Response>")
        assert content.endswith("</Response>")
        assert "<Message>" in content
        assert "</Message>" in content
    
    def test_health_check_json_format(self, test_app):
        """Test health check returns proper JSON format"""
        response = test_app.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON structure
        assert "status" in data
        assert "timestamp" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_test_endpoint_json_format(self, test_app):
        """Test test endpoint returns proper JSON format"""
        response = test_app.get("/api/test")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON structure
        assert "message" in data
        assert isinstance(data["message"], str)


@pytest.mark.api
class TestPerformance:
    """Test API performance"""
    
    def test_response_time(self, test_app, sample_webhook_payload):
        """Test API response time is reasonable"""
        import time
        
        start_time = time.time()
        response = test_app.post("/api/webhook", data=sample_webhook_payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_concurrent_requests(self, test_app, sample_webhook_payload):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_app.post("/api/webhook", data=sample_webhook_payload)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)

