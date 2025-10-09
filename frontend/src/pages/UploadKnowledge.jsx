import React, { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { toast } from '../hooks/use-toast'
import { Upload, FileSpreadsheet, Home, X, Check, ChevronDown } from 'lucide-react'

function UploadKnowledge() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedSystem, setSelectedSystem] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isDragOver, setIsDragOver] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const fileInputRef = useRef(null)

  const systemOptions = [
    { value: 'UMS', label: 'Undercarriage Management System' },
    { value: 'KOMTRAX', label: 'KOMTRAX' }
  ]

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
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv' // .csv
    ]
    const allowedExtensions = ['.xlsx', '.xls', '.csv']
    const maxFileSize = 50 * 1024 * 1024 // 50MB limit

    // Check file type and extension
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      toast.error('Invalid file type. Only Excel (.xlsx, .xls) and CSV files are allowed.')
      return
    }

    if (file.size > maxFileSize) {
      toast.error('File size too large. Maximum file size is 50MB.')
      return
    }

    setSelectedFile(file)
    toast.success('File selected successfully!')
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      processFile(files[0])
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setUploadProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    toast.success('File removed successfully!')
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first.')
      return
    }

    if (!selectedSystem) {
      toast.error('Please select a system type.')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    // Simulate upload progress (since we're not implementing the actual API call yet)
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + Math.random() * 20
      })
    }, 200)

    try {
      // Simulate upload time
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      setTimeout(() => {
        setIsUploading(false)
        setUploadProgress(0)
        setSelectedFile(null)
        setSelectedSystem('')
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        toast.success('Knowledge file uploaded successfully!')
      }, 500)
      
    } catch (error) {
      clearInterval(progressInterval)
      setIsUploading(false)
      setUploadProgress(0)
      toast.error('Upload failed. Please try again.')
    }
  }

  const handleSystemSelect = (system) => {
    setSelectedSystem(system.value)
    setIsDropdownOpen(false)
  }

  const selectedSystemLabel = systemOptions.find(option => option.value === selectedSystem)?.label || 'Select a system'

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Upload Knowledge Files
            </h1>
            <Link to="/">
              <Button variant="outline" size="sm">
                <Home className="h-4 w-4 mr-2" />
                Home
              </Button>
            </Link>
          </div>

          <p className="text-gray-600 mb-8">
            Upload Excel or CSV files containing knowledge data for processing
          </p>

          {/* System Selection Dropdown */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              System Type *
            </label>
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className={`w-full px-4 py-3 text-left bg-white border rounded-lg shadow-sm flex items-center justify-between ${
                  selectedSystem ? 'border-green-300 bg-green-50' : 'border-gray-300'
                } hover:border-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
              >
                <span className={selectedSystem ? 'text-gray-900' : 'text-gray-500'}>
                  {selectedSystemLabel}
                </span>
                <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {isDropdownOpen && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                  {systemOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleSystemSelect(option)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none first:rounded-t-lg last:rounded-b-lg"
                    >
                      <div className="font-medium text-gray-900">{option.label}</div>
                      <div className="text-sm text-gray-500">({option.value})</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* File Upload Area */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Knowledge File *
            </label>
            
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragOver
                  ? 'border-blue-400 bg-blue-50'
                  : selectedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 bg-gray-50 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {selectedFile ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-center">
                    <Check className="h-12 w-12 text-green-500" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                  <Button 
                    onClick={handleRemoveFile}
                    variant="outline"
                    size="sm"
                    className="mt-2"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Remove File
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center">
                    <FileSpreadsheet className="h-12 w-12 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-gray-600">
                      Drop your Excel or CSV file here
                    </p>
                    <p className="text-sm text-gray-500">
                      or click to browse files
                    </p>
                  </div>
                  <Button 
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Choose File
                  </Button>
                  <p className="text-xs text-gray-400">
                    Supported formats: .xlsx, .xls, .csv (Max 50MB)
                  </p>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".xlsx,.xls,.csv"
              multiple={false}
              className="hidden"
            />
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Uploading...</span>
                <span className="text-sm text-gray-500">{Math.round(uploadProgress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Upload Button */}
          <div className="flex gap-4">
            <Button 
              onClick={handleUpload}
              disabled={!selectedFile || !selectedSystem || isUploading}
              className="flex-1"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Knowledge File
                </>
              )}
            </Button>
          </div>

          {/* Instructions */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">Upload Instructions</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Select the appropriate system type (UMS or KOMTRAX)</li>
              <li>• Choose an Excel (.xlsx, .xls) or CSV file containing knowledge data</li>
              <li>• File size must not exceed 50MB</li>
              <li>• Only one file can be uploaded at a time</li>
              <li>• Drag and drop is supported for easier file selection</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadKnowledge