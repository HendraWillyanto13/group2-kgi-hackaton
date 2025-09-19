import React from 'react'
import { Link } from 'react-router-dom'
import { useState, useRef } from 'react'
import { Button } from '../components/ui/button'
import { toast } from '../hooks/use-toast'
import { uploadImages, getDetections, updateObjectsMetadata } from '../lib/api'

function UploadPage() {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [dragCounter, setDragCounter] = useState(0)
  const fileInputRef = useRef(null)

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    processFiles(files)
  }

  const processFiles = (files) => {
    const validFiles = []
    const invalidFiles = []
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    const maxFileSize = 10 * 1024 * 1024 // 10MB limit
    const tooLargeFiles = []

    files.forEach(file => {
      if (!allowedTypes.includes(file.type.toLowerCase())) {
        invalidFiles.push(file.name)
      } else if (file.size > maxFileSize) {
        tooLargeFiles.push(file.name)
      } else {
        validFiles.push(file)
      }
    })

    // Show specific error messages
    if (invalidFiles.length > 0) {
      toast.error(`Invalid file types: ${invalidFiles.join(', ')}. Only JPG, PNG, and GIF formats are allowed.`)
    }
    
    if (tooLargeFiles.length > 0) {
      toast.error(`Files too large: ${tooLargeFiles.join(', ')}. Maximum file size is 10MB.`)
    }

    if (validFiles.length > 0) {
      setSelectedFiles(prevFiles => [...prevFiles, ...validFiles])
    }
  }

  const handleSelectImagesClick = () => {
    fileInputRef.current?.click()
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragCounter(prev => prev + 1)
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragCounter(prev => {
      const newCount = prev - 1
      if (newCount === 0) {
        setIsDragOver(false)
      }
      return newCount
    })
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    setDragCounter(0)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length === 0) {
      toast.error('No files were dropped. Please try again.')
      return
    }
    
    processFiles(files)
  }

  const removeFile = (indexToRemove) => {
    setSelectedFiles(prevFiles => 
      prevFiles.filter((_, index) => index !== indexToRemove)
    )
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0 || isUploading) {
      return
    }

    setIsUploading(true)

    try {
      const result = await uploadImages(selectedFiles)

      // Success: process object detection for each uploaded file
      if (result.files && result.files.length > 0) {
        toast.success(`Upload complete! ${result.files.length} image${result.files.length !== 1 ? 's' : ''} uploaded successfully.`)
        
        // Process object detection for each uploaded file
        for (const fileInfo of result.files) {
          try {
            // Get object detections using the stored filename (without file path)
            const detections = await getDetections(fileInfo.saved_filename);
            
            // Update metadata with object information
            if (detections && detections.boxes) {
              await updateObjectsMetadata(fileInfo.saved_filename, detections.boxes);
              console.log(`Updated metadata for ${fileInfo.saved_filename} with ${detections.boxes.length} detected objects`);
            }
          } catch (error) {
            console.error(`Failed to process detections for ${fileInfo.saved_filename}:`, error);
            // Continue processing other files even if one fails
          }
        }
      }
      
      // Reset files
      setSelectedFiles([])
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      
    } catch (error) {
      // Enhanced error handling with specific error messages
      console.error('Upload failed:', error)
      
      let errorMessage = 'Upload failed. Please try again.'
      
      if (error.response) {
        // Server responded with an error status
        const status = error.response.status
        if (status === 413) {
          errorMessage = 'Files are too large. Please reduce file sizes and try again.'
        } else if (status === 400) {
          errorMessage = 'Invalid file format or corrupted files detected.'
        } else if (status === 500) {
          errorMessage = 'Server error occurred. Please try again later.'
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail
        }
      } else if (error.request) {
        // Request was made but no response received (network error)
        errorMessage = 'Network error. Please check your connection and try again.'
      } else if (error.code === 'ECONNABORTED') {
        // Request timeout
        errorMessage = 'Upload timeout. Please try with smaller files or check your connection.'
      }
      
      toast.error(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Navigation back to home */}
        <div className="mb-6 flex justify-between items-center">
          <Link to="/">
            <Button 
              variant="outline" 
              className="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            >
              ← Back to Home
            </Button>
          </Link>
          <Link to="/files">
            <Button 
              variant="outline"
              className="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            >
              View Uploaded Files →
            </Button>
          </Link>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 space-y-8">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-gray-900">
              Image Upload
            </h1>
            <p className="text-gray-600 text-sm">
              Select one or more images to upload. Only image files are accepted.
            </p>
          </div>
          
          {/* Hidden file input with proper accessibility */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/gif"
            multiple
            onChange={handleFileSelect}
            className="sr-only"
            aria-label="Select image files for upload"
            id="file-upload"
          />
          
          {/* Select Images Button */}
          <div className="text-center">
            <Button 
              onClick={handleSelectImagesClick}
              disabled={isUploading}
              size="lg"
              className="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              aria-describedby="file-upload-help"
            >
              {selectedFiles.length === 0 ? 'Select Images' : 'Choose Different Images'}
            </Button>
            <p id="file-upload-help" className="text-xs text-gray-500 mt-2">
              Click to browse and select image files from your device
            </p>
          </div>

          {/* Upload Button and Progress */}
          {selectedFiles.length > 0 && (
            <div className="space-y-4">
              <div className="text-center">
                <Button
                  onClick={handleUpload}
                  disabled={selectedFiles.length === 0 || isUploading}
                  size="lg"
                  variant={isUploading ? "outline" : "default"}
                  className="focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2 min-w-[120px]"
                  aria-describedby="upload-status"
                >
                  {isUploading ? 'Uploading...' : 'Upload Images'}
                </Button>
              </div>
              
              {isUploading && (
                <div className="space-y-3" role="status" aria-live="polite">
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-600 rounded-full animate-pulse"></div>
                  </div>
                  <p id="upload-status" className="text-center text-sm text-gray-600">
                    Uploading files...
                  </p>
                </div>
              )}
            </div>
          )}

          {/* File List or Drop Zone */}
          <div 
            className={`rounded-lg border-2 border-dashed p-6 transition-all duration-200 ${
              isDragOver 
                ? 'border-blue-400 bg-blue-50 shadow-lg scale-[1.02]' 
                : selectedFiles.length === 0 
                  ? 'border-gray-300 bg-gray-50/50 hover:border-gray-400 hover:bg-gray-50 hover:shadow-sm' 
                  : 'border-gray-200 bg-gray-50/50'
            }`}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            role="button"
            tabIndex={0}
            onClick={selectedFiles.length === 0 ? handleSelectImagesClick : undefined}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && selectedFiles.length === 0) {
                e.preventDefault()
                handleSelectImagesClick()
              }
            }}
            aria-label={selectedFiles.length === 0 ? "Click or drag files to upload" : "Selected files"}
          >
            {selectedFiles.length === 0 ? (
              <div className="text-center py-12">
                <div className="mx-auto w-16 h-16 text-gray-400 mb-4">
                  {isDragOver ? (
                    <svg fill="none" stroke="currentColor" viewBox="0 0 48 48" className="animate-pulse">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M24 8v32m-8-8l8 8 8-8"
                      />
                    </svg>
                  ) : (
                    <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1}
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      />
                    </svg>
                  )}
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {isDragOver ? 'Drop files here' : 'Drop files here or click to select'}
                </h3>
                <p className="text-sm text-gray-500 mb-4">
                  {isDragOver ? 'Release to upload your images' : 'Drag and drop image files, or click to browse'}
                </p>
                <p className="text-xs text-gray-400">
                  Supports JPG, PNG, and GIF formats (max 10MB each)
                </p>
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Selected Files
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-80 overflow-y-auto">
                  {selectedFiles.map((file, index) => (
                    <FilePreview 
                      key={`${file.name}-${index}`} 
                      file={file} 
                      index={index}
                      formatFileSize={formatFileSize} 
                      onRemove={removeFile}
                      disabled={isUploading}
                    />
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
                  <button
                    onClick={handleSelectImagesClick}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                    disabled={isUploading}
                  >
                    + Add more images
                  </button>
                  <button
                    onClick={() => setSelectedFiles([])}
                    className="text-sm text-red-600 hover:text-red-700 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded"
                    disabled={isUploading}
                  >
                    Clear all
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// File preview component with image thumbnail and remove button
function FilePreview({ file, index, formatFileSize, onRemove, disabled }) {
  const [imageUrl, setImageUrl] = useState(null)

  React.useEffect(() => {
    if (file && file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file)
      setImageUrl(url)
      
      // Cleanup function to revoke object URL
      return () => URL.revokeObjectURL(url)
    }
  }, [file])

  const handleRemove = (e) => {
    e.stopPropagation()
    if (!disabled) {
      onRemove(index)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3 hover:shadow-sm transition-shadow relative group">
      {/* Remove button */}
      <button
        onClick={handleRemove}
        disabled={disabled}
        className="absolute -top-2 -right-2 z-10 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        aria-label={`Remove ${file.name}`}
        type="button"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div className="aspect-square w-full mb-3 bg-gray-100 rounded-lg overflow-hidden">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={file.name}
            className="w-full h-full object-cover"
            onError={() => setImageUrl(null)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
            </svg>
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-900 truncate" title={file.name}>
          {file.name}
        </p>
        <p className="text-xs text-gray-500">
          {formatFileSize(file.size)} • {file.type.split('/')[1]?.toUpperCase()}
        </p>
      </div>
    </div>
  )
}

export default UploadPage