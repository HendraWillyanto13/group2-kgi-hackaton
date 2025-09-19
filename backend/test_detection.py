#!/usr/bin/env python3
"""
Test script for the detection endpoint implementation.
This tests the core normalization logic.
"""

import json

def normalize_detection_response(api_response):
    """
    Normalize Azure Computer Vision API response to the expected format.
    (Simplified version without logging for testing)
    """
    try:
        boxes = []
        
        # Get image dimensions for normalization
        metadata = api_response.get("metadata", {})
        img_width = metadata.get("width", 1)
        img_height = metadata.get("height", 1)
        
        # Extract objects from the API response
        objects = api_response.get("objects", [])
        
        for obj in objects:
            # Extract bounding box rectangle
            rect = obj.get("rectangle", {})
            
            # Normalize coordinates to 0-1 range
            x = rect.get("x", 0) / img_width
            y = rect.get("y", 0) / img_height
            w = rect.get("w", 0) / img_width
            h = rect.get("h", 0) / img_height
            
            box = {
                "label": obj.get("object", "unknown"),
                "x": round(x, 4),
                "y": round(y, 4),
                "w": round(w, 4),
                "h": round(h, 4),
                "score": round(obj.get("confidence", 0.0), 4)
            }
            
            boxes.append(box)
        
        return {"boxes": boxes}
        
    except Exception as e:
        print(f"Error normalizing detection response: {str(e)}")
        return {"boxes": []}

def test_normalize_detection_response():
    """Test the detection response normalization function."""
    
    # Mock Azure Computer Vision API response
    mock_api_response = {
        "objects": [
            {
                "rectangle": {"x": 100, "y": 50, "w": 200, "h": 150},
                "object": "person",
                "confidence": 0.85
            },
            {
                "rectangle": {"x": 300, "y": 200, "w": 100, "h": 80},
                "object": "car",
                "confidence": 0.92
            }
        ],
        "metadata": {
            "width": 800,
            "height": 600
        }
    }
    
    # Test normalization
    result = normalize_detection_response(mock_api_response)
    
    print("Test normalize_detection_response:")
    print(f"Output: {json.dumps(result, indent=2)}")
    
    # Verify the structure
    assert "boxes" in result
    assert len(result["boxes"]) == 2
    
    # Check first box
    box1 = result["boxes"][0]
    assert box1["label"] == "person"
    assert box1["x"] == 0.125  # 100/800
    assert box1["y"] == 0.0833  # 50/600 rounded
    assert box1["w"] == 0.25    # 200/800
    assert box1["h"] == 0.25    # 150/600
    assert box1["score"] == 0.85
    
    print("✅ normalize_detection_response test passed!")

def test_error_scenarios():
    """Test error scenarios for normalization."""
    
    # Test with empty response
    empty_response = {"objects": [], "metadata": {"width": 800, "height": 600}}
    result = normalize_detection_response(empty_response)
    print(f"\nTest empty response: {json.dumps(result)}")
    assert result == {"boxes": []}
    
    # Test with malformed response
    malformed_response = {"invalid": "data"}
    result = normalize_detection_response(malformed_response)
    print(f"Test malformed response: {json.dumps(result)}")
    assert result == {"boxes": []}
    
    print("✅ Error scenario tests passed!")

if __name__ == "__main__":
    print("Testing Detection Endpoint Implementation")
    print("=" * 50)
    
    try:
        test_normalize_detection_response()
        test_error_scenarios()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()