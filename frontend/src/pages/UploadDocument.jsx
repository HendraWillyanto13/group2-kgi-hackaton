import React, { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { toast } from '../hooks/use-toast'
import { uploadFile } from '../lib/api'
import { Upload, FileText, Home, X, Check } from 'lucide-react'

function UploadDocument() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef(null)

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      processFile(file)
    }
  }

  const processFile = (file) => {
    const allowedTypes = ['application/pdf', 'text/plain']
    const allowedExtensions = ['.pdf', '.txt']
    const maxFileSize = 50 * 1024 * 1024 // 50MB limit

    // Check file type and extension
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      toast.error('Invalid file type. Only PDF and TXT files are allowed.')
      return
    }

    if (file.size > maxFileSize) {
      toast.error('File size too large. Maximum file size is 50MB.')
      return
    }

    setSelectedFile(file)
    toast.success('File selected successfully!')
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      processFile(files[0]) // Only take the first file
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first.')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    try {
      await uploadFile(selectedFile, (progress) => {
        setUploadProgress(progress)
      })

      // Success notification with green checkmark
      toast.success(
        <div className="flex items-center gap-2">
          <Check className="h-4 w-4 text-green-500" />
          Upload Successful
        </div>
      )
      
      // Reset form
      setSelectedFile(null)
      setUploadProgress(0)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      console.error('Upload failed:', error)
      
      // Failed notification with red X
      toast.error(
        <div className="flex items-center gap-2">
          <X className="h-4 w-4 text-red-500" />
          Upload Failed
        </div>
      )
      setUploadProgress(0)
    } finally {
      setIsUploading(false)
    }
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Document</h1>
            <p className="text-gray-600">
              Upload your PDF or TXT files for processing
            </p>
          </div>

          {/* File Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <div className="space-y-2">
              <p className="text-xl font-medium text-gray-900">
                Drop your file here, or{' '}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-blue-600 hover:text-blue-500 underline"
                >
                  browse
                </button>
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF and TXT files up to 50MB
              </p>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.txt"
              multiple={false}
              className="hidden"
            />
          </div>

          {/* Selected File Display */}
          {selectedFile && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={removeFile}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Progress Bar */}
              {isUploading && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-8 space-y-4">
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="w-full gap-2 text-lg px-6 py-4 h-auto"
            >
              <Upload className="h-6 w-6" />
              {isUploading ? 'Uploading...' : 'Upload Document'}
            </Button>

            <Link to="/" className="block">
              <Button variant="outline" className="w-full gap-2 text-lg px-6 py-4 h-auto">
                <Home className="h-6 w-6" />
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadDocument