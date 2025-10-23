#!/usr/bin/env python3
"""
Test script for the new image analysis endpoint
"""

import requests
import json
import time
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/image-analysis/analyze"

# Sample image URLs (replace with actual bucket URLs)
SAMPLE_IMAGE_URLS = [
    "https://example.com/patient_scalp_front.jpg",
    "https://example.com/patient_scalp_top.jpg",
    "https://example.com/patient_scalp_side.jpg"
]

def test_image_analysis_endpoint():
    """Test the image analysis endpoint with sample data"""
    
    print("🧪 Testing Image Analysis Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "image_urls": SAMPLE_IMAGE_URLS,
        "patient_id": "test-patient-123",
        "analysis_type": "comprehensive",
        "include_pdf": True
    }
    
    print(f"📊 Test Data:")
    print(f"   Images: {len(test_data['image_urls'])}")
    print(f"   Patient ID: {test_data['patient_id']}")
    print(f"   Analysis Type: {test_data['analysis_type']}")
    print(f"   Include PDF: {test_data['include_pdf']}")
    print()
    
    try:
        print("🚀 Sending request to endpoint...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout for image analysis
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Request completed in {duration:.2f} seconds")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print()
            
            if result.get("success"):
                data = result.get("data", {})
                analysis = data.get("analysis", {})
                
                print("📋 Analysis Results:")
                print(f"   Report ID: {data.get('report_id', 'N/A')}")
                print(f"   Images Analyzed: {data.get('images_analyzed', 0)}")
                print(f"   Norwood Scale: {analysis.get('norwood_scale', 'N/A')}")
                print(f"   Graft Estimate: {analysis.get('graft_estimate', {}).get('min', 'N/A')} - {analysis.get('graft_estimate', {}).get('max', 'N/A')}")
                print(f"   Cost Estimate: ${analysis.get('cost_estimate', {}).get('min', 'N/A')} - ${analysis.get('cost_estimate', {}).get('max', 'N/A')}")
                print(f"   Procedure Type: {analysis.get('procedure_type', 'N/A')}")
                print()
                
                # Check if PDF was generated
                if data.get('pdf_content'):
                    print("📄 PDF Report Generated: Yes")
                    pdf_size = len(data['pdf_content']) / 1024  # Size in KB
                    print(f"   PDF Size: {pdf_size:.1f} KB")
                else:
                    print("📄 PDF Report Generated: No")
                
                print()
                print("📝 Analysis Text Preview:")
                analysis_text = analysis.get('analysis', 'No analysis available')
                preview = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
                print(f"   {preview}")
                
            else:
                print("❌ Analysis failed:")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        else:
            print("❌ Request failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (120 seconds)")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the server running?")
        print(f"   Make sure to start the server: python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def test_quick_analysis():
    """Test the quick analysis endpoint"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Quick Analysis Endpoint")
    print("=" * 50)
    
    test_data = {
        "image_urls": SAMPLE_IMAGE_URLS[:1],  # Just one image for quick test
        "patient_id": "test-patient-456",
        "analysis_type": "quick",
        "include_pdf": False
    }
    
    try:
        print("🚀 Sending quick analysis request...")
        
        response = requests.post(
            f"{BASE_URL}/api/image-analysis/analyze/quick",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Quick analysis successful!")
                data = result.get("data", {})
                print(f"   Report ID: {data.get('report_id', 'N/A')}")
                print(f"   Images Analyzed: {data.get('images_analyzed', 0)}")
            else:
                print(f"❌ Quick analysis failed: {result.get('error')}")
        else:
            print(f"❌ Quick analysis request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Quick analysis error: {str(e)}")

def test_health_check():
    """Test the health check endpoint"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Health Check Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/image-analysis/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Service: {result.get('service')}")
            print(f"   Version: {result.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

def main():
    """Run all tests"""
    print("🔬 Image Analysis Endpoint Test Suite")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Test health check first
    test_health_check()
    
    # Test main analysis endpoint
    test_image_analysis_endpoint()
    
    # Test quick analysis
    test_quick_analysis()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
