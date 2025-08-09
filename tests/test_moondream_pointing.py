"""
Test Moondream Vision Model for Coordinate Detection
Tests the Moondream server's ability to find specific elements in images and return their coordinates.
"""

import requests
import base64
import json
from PIL import Image
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def encode_image_to_base64(image_path):
    """Encode image to base64 string for API requests."""
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            # Determine image type from file extension
            if image_path.lower().endswith('.png'):
                return f"data:image/png;base64,{encoded}"
            else:
                return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        raise Exception(f"Failed to encode image: {str(e)}")

def test_moondream_pointing():
    """Test Moondream's pointing capability with ESPN app icon detection."""
    print("🔍 Testing Moondream Vision Model - ESPN App Icon Detection")
    print("=" * 70)
    
    # Configuration
    image_path = "./test_image.png"
    moondream_url = "http://localhost:2020/v1/point"
    target_object = "ESPN app icon"
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return False
    
    try:
        # Load image and get dimensions
        print(f"📂 Loading image: {image_path}")
        image = Image.open(image_path)
        width, height = image.size
        print(f"📏 Image dimensions: {width} x {height} pixels")
        
        # Encode image to base64
        print("🔄 Encoding image to base64...")
        image_base64 = encode_image_to_base64(image_path)
        print(f"✅ Image encoded successfully ({len(image_base64)} characters)")
        
        # Prepare API request
        print(f"🎯 Searching for: {target_object}")
        point_data = {
            "image_url": image_base64,
            "object": target_object
        }
        
        # Send request to Moondream
        print(f"📡 Sending request to Moondream server: {moondream_url}")
        response = requests.post(moondream_url, json=point_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        print("✅ Moondream response received!")
        print("📋 Raw Response:")
        print(json.dumps(result, indent=2))
        
        # Process coordinates
        if "points" in result and result["points"]:
            points = result["points"]
            print(f"\n🎯 Found {len(points)} point(s) for '{target_object}':")
            
            for i, point in enumerate(points, 1):
                # Get normalized coordinates (0-1 range)
                norm_x = point.get("x", 0)
                norm_y = point.get("y", 0)
                
                # Convert to pixel coordinates
                pixel_x = int(norm_x * width)
                pixel_y = int(norm_y * height)
                
                print(f"\n📍 Point {i}:")
                print(f"   Normalized coordinates: ({norm_x:.4f}, {norm_y:.4f})")
                print(f"   Pixel coordinates: ({pixel_x}, {pixel_y})")
                print(f"   Relative position: {norm_x*100:.1f}% from left, {norm_y*100:.1f}% from top")
                
                # Validate coordinates are within image bounds
                if 0 <= pixel_x <= width and 0 <= pixel_y <= height:
                    print(f"   ✅ Coordinates are within image bounds")
                else:
                    print(f"   ⚠️ Warning: Coordinates are outside image bounds!")
        
        elif "error" in result:
            print(f"❌ Moondream Error: {result['error']}")
            return False
        
        else:
            print(f"❌ No points found for '{target_object}'")
            print("💡 Try different search terms like:")
            print("   - 'ESPN app'")
            print("   - 'red circular icon'") 
            print("   - 'app with white E letter'")
            return False
        
        # Additional response information
        if "request_id" in result:
            print(f"\n🆔 Request ID: {result['request_id']}")
        
        print("\n" + "=" * 70)
        print("✅ Moondream pointing test completed successfully!")
        
        # Instructions for browser integration
        print("\n💡 For browser automation integration:")
        print(f"   Use click({pixel_x}, {pixel_y}) to click on the ESPN app")
        print("   The coordinates are ready for browser automation tools!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Moondream server")
        print("💡 Make sure Moondream is running on http://localhost:2020")
        return False
    
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        print("💡 Moondream might be processing - try again in a moment")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_moondream_health():
    """Test if Moondream server is accessible."""
    print("🏥 Testing Moondream server health...")
    try:
        # Try to connect to the server
        health_url = "http://localhost:2020/health"
        response = requests.get(health_url, timeout=5)
        print(f"✅ Moondream server is responsive (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Moondream server is not accessible")
        return False
    except Exception as e:
        print(f"⚠️ Health check failed: {str(e)}")
        return False

def main():
    """Run all Moondream tests."""
    print("🚀 Moondream Vision Model Testing Suite")
    print("=" * 70)
    
    # Test server health first
    if not test_moondream_health():
        print("\n💡 Setup Instructions:")
        print("1. Make sure Moondream server is running on localhost:2020")
        print("2. Check that the server accepts requests on /v1/point endpoint")
        return
    
    print()
    
    # Test pointing capability
    success = test_moondream_pointing()
    
    if success:
        print("\n🎊 All tests passed! Moondream is ready for browser automation integration.")
        print("\n🔧 Next steps:")
        print("1. Integrate pointing into browser automation tools")
        print("2. Create intelligent click tool that finds elements by description")
        print("3. Test with real browser screenshots")
    else:
        print("\n❌ Tests failed. Please check the Moondream server and image.")

if __name__ == "__main__":
    main()
