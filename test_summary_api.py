#!/usr/bin/env python3
"""
Test script for the text summarization API endpoints.
Run this script to test the Google API integration.
"""

import asyncio
import json
from app.services.summary_service import summary_service

async def test_summary_service():
    """Test the summary service functionality."""
    
    # Sample text for testing
    sample_text = """
    Artificial Intelligence (AI) has revolutionized numerous industries and continues to shape our daily lives. 
    From voice assistants like Siri and Alexa to recommendation systems on Netflix and Amazon, AI is everywhere. 
    Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions 
    that were previously impossible. In healthcare, AI helps doctors diagnose diseases more accurately by analyzing 
    medical images and patient data. In transportation, autonomous vehicles are becoming a reality, promising 
    safer and more efficient travel. However, AI also presents challenges such as job displacement, privacy concerns, 
    and the need for ethical guidelines. As we move forward, it's crucial to balance the benefits of AI with 
    responsible development and deployment practices.
    """
    
    print("🤖 Testing Google API Text Summarization Service")
    print("=" * 60)
    
    # Test 1: Basic Text Summarization
    print("\n📝 Test 1: Basic Text Summarization")
    print("-" * 40)
    
    result = await summary_service.summarize_text(
        text=sample_text,
        max_length=50,
        style="concise"
    )
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Summary: {result['summary']}")
        print(f"📊 Word count: {result['word_count']} (original: {result['original_word_count']})")
        print(f"📈 Compression ratio: {result['compression_ratio']}")
    
    # Test 2: Key Points Extraction
    print("\n🔑 Test 2: Key Points Extraction")
    print("-" * 40)
    
    result = await summary_service.extract_key_points(
        text=sample_text,
        num_points=5
    )
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Key Points:")
        for i, point in enumerate(result['key_points'], 1):
            print(f"   {i}. {point}")
        print(f"📊 Extracted {result['extracted_count']} points from {result['word_count']} words")
    
    # Test 3: Sentiment Analysis
    print("\n😊 Test 3: Sentiment Analysis")
    print("-" * 40)
    
    result = await summary_service.analyze_sentiment(text=sample_text)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Sentiment: {result['sentiment']}")
        print(f"📊 Confidence: {result['confidence']}%")
        print(f"💭 Explanation: {result['explanation']}")
    
    # Test 4: Different Summary Styles
    print("\n🎨 Test 4: Different Summary Styles")
    print("-" * 40)
    
    styles = ["concise", "detailed", "bullet_points"]
    for style in styles:
        result = await summary_service.summarize_text(
            text=sample_text,
            max_length=30,
            style=style
        )
        
        if result.get("error"):
            print(f"❌ {style.title()} style error: {result['error']}")
        else:
            print(f"✅ {style.title()} style summary:")
            print(f"   {result['summary']}")
            print(f"   Word count: {result['word_count']}")
        print()

async def test_api_endpoints():
    """Test the API endpoints using HTTP requests."""
    import httpx
    
    base_url = "http://localhost:8000/api/v1/summary"
    
    sample_text = """
    Climate change is one of the most pressing challenges of our time. Rising global temperatures, 
    melting ice caps, and extreme weather events are clear indicators of environmental changes. 
    Scientists agree that human activities, particularly greenhouse gas emissions, are the primary 
    drivers of climate change. To address this crisis, we need immediate action on multiple fronts: 
    reducing carbon emissions, transitioning to renewable energy sources, and implementing sustainable 
    practices in agriculture and industry. International cooperation is essential, as climate change 
    affects all nations regardless of their contribution to the problem. The Paris Agreement represents 
    a significant step forward, but more ambitious targets and faster implementation are needed. 
    Individual actions, such as reducing energy consumption and supporting green technologies, 
    also play a crucial role in combating climate change.
    """
    
    print("🌐 Testing API Endpoints")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test summarization endpoint
        print("\n📝 Testing /summarize endpoint")
        print("-" * 40)
        
        try:
            response = await client.post(
                f"{base_url}/summarize",
                json={
                    "text": sample_text,
                    "max_length": 40,
                    "style": "concise"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Summary: {data['summary']}")
                print(f"📊 Compression ratio: {data['compression_ratio']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("💡 Make sure the FastAPI server is running on http://localhost:8000")
        
        # Test key points endpoint
        print("\n🔑 Testing /key-points endpoint")
        print("-" * 40)
        
        try:
            response = await client.post(
                f"{base_url}/key-points",
                json={
                    "text": sample_text,
                    "num_points": 4
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Key Points:")
                for i, point in enumerate(data['key_points'], 1):
                    print(f"   {i}. {point}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        # Test health endpoint
        print("\n🏥 Testing /health endpoint")
        print("-" * 40)
        
        try:
            response = await client.get(f"{base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['status']}")
                print(f"🔑 Google API configured: {data['google_api_configured']}")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

def main():
    """Main function to run all tests."""
    print("🚀 Starting Text Summarization API Tests")
    print("=" * 60)
    
    # Test the service directly
    asyncio.run(test_summary_service())
    
    # Test API endpoints
    asyncio.run(test_api_endpoints())
    
    print("\n✨ Tests completed!")
    print("\n📋 Next steps:")
    print("1. Set your GOOGLE_API_KEY in the .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the server: python run.py")
    print("4. Visit http://localhost:8000/docs to see the API documentation")

if __name__ == "__main__":
    main()
