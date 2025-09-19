import React, { useRef, useEffect, useState } from 'react'

/**
 * DetectionOverlay Component
 * 
 * Renders an image with bounding box overlays for object detections
 * 
 * @param {Object} props
 * @param {string} props.imageUrl - URL of the image to display
 * @param {Array} props.boxes - Array of detection boxes with format:
 *   [{ label: string, x: number, y: number, w: number, h: number, score: number }]
 *   where x, y, w, h are normalized coordinates (0-1)
 */
function DetectionOverlay({ imageUrl, boxes = [] }) {
  const containerRef = useRef(null)
  const imageRef = useRef(null)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })
  const [imageLoaded, setImageLoaded] = useState(false)

  // Update image dimensions when image loads
  const handleImageLoad = () => {
    if (imageRef.current) {
      const { clientWidth, clientHeight } = imageRef.current
      setImageDimensions({ width: clientWidth, height: clientHeight })
      setImageLoaded(true)
    }
  }

  // Update dimensions on window resize
  useEffect(() => {
    const handleResize = () => {
      if (imageRef.current && imageLoaded) {
        const { clientWidth, clientHeight } = imageRef.current
        setImageDimensions({ width: clientWidth, height: clientHeight })
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [imageLoaded])

  // Convert normalized coordinates to pixel coordinates
  const convertToPixels = (box) => {
    const { x, y, w, h } = box
    return {
      left: x * imageDimensions.width,
      top: y * imageDimensions.height,
      width: w * imageDimensions.width,
      height: h * imageDimensions.height,
    }
  }

  return (
    <div 
      ref={containerRef}
      className="relative inline-block max-w-full"
      style={{ maxHeight: '80vh' }}
    >
      {/* Image */}
      <img
        ref={imageRef}
        src={imageUrl}
        alt="Uploaded image with detections"
        className="max-w-full h-auto block"
        onLoad={handleImageLoad}
        onError={() => setImageLoaded(false)}
      />
      
      {/* Bounding box overlays */}
      {imageLoaded && boxes.length > 0 && (
        <div className="absolute inset-0">
          {boxes.map((box, index) => {
            const pixelCoords = convertToPixels(box)
            const confidencePercent = Math.round(box.score * 100)
            
            return (
              <div
                key={index}
                className="absolute border-2 border-red-500 bg-red-500 bg-opacity-10"
                style={{
                  left: `${pixelCoords.left}px`,
                  top: `${pixelCoords.top}px`,
                  width: `${pixelCoords.width}px`,
                  height: `${pixelCoords.height}px`,
                }}
              >
                {/* Label with confidence score */}
                <div 
                  className="absolute -top-6 left-0 bg-red-500 text-white text-xs px-2 py-1 rounded whitespace-nowrap font-medium shadow-lg"
                  style={{
                    fontSize: '11px',
                    lineHeight: '1.2',
                  }}
                >
                  {box.label} ({confidencePercent}%)
                </div>
              </div>
            )
          })}
        </div>
      )}
      
      {/* Detection count indicator */}
      {imageLoaded && boxes.length > 0 && (
        <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-sm px-3 py-1 rounded-full">
          {boxes.length} object{boxes.length !== 1 ? 's' : ''} detected
        </div>
      )}
    </div>
  )
}

export default DetectionOverlay