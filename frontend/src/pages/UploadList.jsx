import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { toast } from '../hooks/use-toast'
import { getUploadedFiles, deleteFiles, getFileUrl, getDetections } from '../lib/api'
import DetectionOverlay from '../components/DetectionOverlay'

function UploadList() {
  const [files, setFiles] = useState([])
  const [selectedFiles, setSelectedFiles] = useState(new Set())
  const [isLoading, setIsLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  
  // Date filter state
  const [dateFilter, setDateFilter] = useState({ fromDate: '', toDate: '' })
  const [showDateFilter, setShowDateFilter] = useState(false)
  
  // Object filter state
  const [objectFilter, setObjectFilter] = useState('')
  const [showObjectFilter, setShowObjectFilter] = useState(false)
  
  // Sort state
  const [sortBy, setSortBy] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')
  const [showSortOptions, setShowSortOptions] = useState(false)
  
  // Detection modal state
  const [selectedImage, setSelectedImage] = useState(null)
  const [detectionResults, setDetectionResults] = useState(null)
  const [isDetecting, setIsDetecting] = useState(false)
  const [showDetectionModal, setShowDetectionModal] = useState(false)
  
  // Metadata state
  const [uploadsMetadata, setUploadsMetadata] = useState({})
  const [isLoadingMetadata, setIsLoadingMetadata] = useState(true)

  useEffect(() => {
    loadFiles()
    loadMetadata()
  }, [])

  const loadFiles = async () => {
    try {
      setIsLoading(true)
      const response = await getUploadedFiles()
      setFiles(response.files || [])
    } catch (error) {
      console.error('Error loading files:', error)
      toast.error('Failed to load uploaded files')
      setFiles([])
    } finally {
      setIsLoading(false)
    }
  }

  const loadMetadata = async () => {
    try {
      setIsLoadingMetadata(true)
      // Try to fetch the metadata from the backend
      const response = await fetch('http://localhost:8000/uploads-metadata.json')
      if (response.ok) {
        const metadata = await response.json()
        // Convert to a map for easier lookup by stored_filename
        const metadataMap = {}
        metadata.uploads?.forEach(upload => {
          metadataMap[upload.stored_filename] = upload
        })
        setUploadsMetadata(metadataMap)
      }
    } catch (error) {
      console.error('Error loading metadata:', error)
      // Don't show error toast since metadata is optional for display
    } finally {
      setIsLoadingMetadata(false)
    }
  }

  const handleFileSelect = (filename, isSelected) => {
    const newSelected = new Set(selectedFiles)
    if (isSelected) {
      newSelected.add(filename)
    } else {
      newSelected.delete(filename)
    }
    setSelectedFiles(newSelected)
  }

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedFiles(new Set(currentFiles.map(file => file.filename)))
    } else {
      setSelectedFiles(new Set())
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedFiles.size === 0) {
      toast.error('No files selected')
      return
    }

    setShowDeleteConfirm(true)
  }

  const confirmDelete = async () => {
    try {
      setIsDeleting(true)
      setShowDeleteConfirm(false)
      
      const filesToDelete = Array.from(selectedFiles)
      const response = await deleteFiles(filesToDelete)
      
      if (response.total_deleted > 0) {
        toast.success(`Delete success: ${response.total_deleted} file${response.total_deleted !== 1 ? 's' : ''} deleted`)
        setSelectedFiles(new Set())
        await loadFiles() // Reload the file list
      } else {
        toast.error('No files were deleted')
      }
      
      if (response.errors && response.errors.length > 0) {
        console.warn('Delete errors:', response.errors)
      }
      
    } catch (error) {
      console.error('Error deleting files:', error)
      toast.error('Failed to delete files')
    } finally {
      setIsDeleting(false)
    }
  }

  const cancelDelete = () => {
    setShowDeleteConfirm(false)
  }

  const handleDetectObjects = async (filename) => {
    try {
      setIsDetecting(true)
      setSelectedImage(filename)
      
      const result = await getDetections(filename)
      setDetectionResults(result)
      setShowDetectionModal(true)
      
      toast.success('Object detection completed!')
    } catch (error) {
      console.error('Error detecting objects:', error)
      toast.error('Failed to detect objects in image')
    } finally {
      setIsDetecting(false)
    }
  }

  const closeDetectionModal = () => {
    setShowDetectionModal(false)
    setSelectedImage(null)
    setDetectionResults(null)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000)
    const day = date.getDate().toString().padStart(2, '0')
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const month = monthNames[date.getMonth()]
    const year = date.getFullYear()
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${day}-${month}-${year} ${hours}:${minutes}`
  }

  // Pagination calculations with filtering and sorting
  const filteredFiles = files.filter(file => {
    // Date filter
    if (dateFilter.fromDate || dateFilter.toDate) {
      const fileDate = new Date(file.modified * 1000)
      const fromDate = dateFilter.fromDate ? new Date(dateFilter.fromDate) : null
      const toDate = dateFilter.toDate ? new Date(dateFilter.toDate) : null
      
      // Set time to start/end of day for accurate comparison
      if (fromDate) fromDate.setHours(0, 0, 0, 0)
      if (toDate) toDate.setHours(23, 59, 59, 999)
      
      if (fromDate && fileDate < fromDate) return false
      if (toDate && fileDate > toDate) return false
    }
    
    // Object filter
    if (objectFilter.trim()) {
      const metadata = uploadsMetadata[file.filename]
      if (!metadata || !metadata.objects) return false
      
      const hasMatchingObject = metadata.objects.some(obj => 
        obj.label.toLowerCase().includes(objectFilter.toLowerCase().trim())
      )
      if (!hasMatchingObject) return false
    }
    
    return true
  }).sort((a, b) => {
    let comparison = 0
    
    if (sortBy === 'date') {
      comparison = a.modified - b.modified
    } else if (sortBy === 'size') {
      comparison = a.size - b.size
    } else if (sortBy === 'filename') {
      comparison = a.filename.toLowerCase().localeCompare(b.filename.toLowerCase())
    }
    
    return sortOrder === 'asc' ? comparison : -comparison
  })
  
  const totalPages = Math.ceil(filteredFiles.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentFiles = filteredFiles.slice(startIndex, endIndex)

  const handlePageChange = (page) => {
    setCurrentPage(page)
    setSelectedFiles(new Set()) // Clear selections when changing pages
  }

  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage)
    setCurrentPage(1) // Reset to first page
    setSelectedFiles(new Set()) // Clear selections
  }

  const handleDateFilterChange = (field, value) => {
    setDateFilter(prev => ({ ...prev, [field]: value }))
    setCurrentPage(1) // Reset to first page when filtering
    setSelectedFiles(new Set()) // Clear selections
  }

  const clearDateFilter = () => {
    setDateFilter({ fromDate: '', toDate: '' })
    setCurrentPage(1)
    setSelectedFiles(new Set())
  }

  const handleObjectFilterChange = (value) => {
    setObjectFilter(value)
    setCurrentPage(1) // Reset to first page when filtering
    setSelectedFiles(new Set()) // Clear selections
  }

  const clearObjectFilter = () => {
    setObjectFilter('')
    setCurrentPage(1)
    setSelectedFiles(new Set())
  }

  const handleSortChange = (newSortBy) => {
    if (sortBy === newSortBy) {
      // Toggle sort order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // Set new sort field with default order
      setSortBy(newSortBy)
      setSortOrder(newSortBy === 'filename' ? 'asc' : 'desc')
    }
    setCurrentPage(1)
    setSelectedFiles(new Set())
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading files...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          {/* Top section with back button and title */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <Link to="/upload">
                <Button variant="outline" size="sm">
                  ← Back to Upload
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Uploaded Files</h1>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-sm text-gray-600">
                  <span>
                    {files.length} file{files.length !== 1 ? 's' : ''} uploaded
                    {filteredFiles.length !== files.length && (
                      <span className="text-blue-600 ml-1">
                        ({filteredFiles.length} filtered)
                      </span>
                    )}
                  </span>
                  {filteredFiles.length > 0 && (
                    <>
                      <span className="hidden sm:inline">•</span>
                      <span>
                        Showing {startIndex + 1}-{Math.min(endIndex, filteredFiles.length)} of {filteredFiles.length}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Filter and pagination controls */}
          {files.length > 0 && (
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white rounded-lg shadow p-4">
              {/* Left side - Filter and Sort controls */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <button
                  onClick={() => setShowDateFilter(!showDateFilter)}
                  className={`px-3 py-2 text-sm rounded-md border transition-colors whitespace-nowrap ${
                    showDateFilter || dateFilter.fromDate || dateFilter.toDate
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  📅 Filter by Date
                </button>
                
                <button
                  onClick={() => setShowObjectFilter(!showObjectFilter)}
                  className={`px-3 py-2 text-sm rounded-md border transition-colors whitespace-nowrap ${
                    showObjectFilter || objectFilter.trim()
                      ? 'bg-purple-600 text-white border-purple-600'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  🏷️ Filter by Objects
                </button>
                
                <button
                  onClick={() => setShowSortOptions(!showSortOptions)}
                  className={`px-3 py-2 text-sm rounded-md border transition-colors whitespace-nowrap ${
                    showSortOptions
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  📊 Sort by {sortBy === 'date' ? 'Date' : sortBy === 'size' ? 'Size' : 'Name'} ({sortOrder === 'asc' ? '↑' : '↓'})
                </button>
              </div>
              
              {/* Right side - Items per page selector */}
              <div className="flex items-center gap-2 text-sm">
                <label htmlFor="items-per-page" className="text-gray-700 whitespace-nowrap">
                  Images per page:
                </label>
                <select
                  id="items-per-page"
                  value={itemsPerPage}
                  onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Date Filter Panel */}
        {showDateFilter && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 mb-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
              <div className="flex-1">
                <label htmlFor="from-date" className="block text-sm font-medium text-gray-700 mb-1">
                  From Date
                </label>
                <input
                  id="from-date"
                  type="date"
                  value={dateFilter.fromDate}
                  onChange={(e) => handleDateFilterChange('fromDate', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="flex-1">
                <label htmlFor="to-date" className="block text-sm font-medium text-gray-700 mb-1">
                  To Date
                </label>
                <input
                  id="to-date"
                  type="date"
                  value={dateFilter.toDate}
                  onChange={(e) => handleDateFilterChange('toDate', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={clearDateFilter}
                  variant="outline"
                  size="sm"
                  disabled={!dateFilter.fromDate && !dateFilter.toDate}
                >
                  Clear
                </Button>
                <Button
                  onClick={() => setShowDateFilter(false)}
                  variant="outline"
                  size="sm"
                >
                  Close
                </Button>
              </div>
            </div>
            
            {(dateFilter.fromDate || dateFilter.toDate) && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Active Filter:</span>
                  {dateFilter.fromDate && (
                    <span className="ml-2">From: {new Date(dateFilter.fromDate).toLocaleDateString()}</span>
                  )}
                  {dateFilter.toDate && (
                    <span className="ml-2">To: {new Date(dateFilter.toDate).toLocaleDateString()}</span>
                  )}
                  <span className="ml-2 text-blue-600">
                    ({filteredFiles.length} file{filteredFiles.length !== 1 ? 's' : ''} found)
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Object Filter Panel */}
        {showObjectFilter && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 mb-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
              <div className="flex-1">
                <label htmlFor="object-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Search by detected objects
                </label>
                <input
                  id="object-filter"
                  type="text"
                  value={objectFilter}
                  onChange={(e) => handleObjectFilterChange(e.target.value)}
                  placeholder="Type object name (e.g., person, car, laptop)"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={clearObjectFilter}
                  variant="outline"
                  size="sm"
                  disabled={!objectFilter.trim()}
                >
                  Clear
                </Button>
                <Button
                  onClick={() => setShowObjectFilter(false)}
                  variant="outline"
                  size="sm"
                >
                  Close
                </Button>
              </div>
            </div>
            
            {objectFilter.trim() && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Active Filter:</span>
                  <span className="ml-2">Objects containing "{objectFilter}"</span>
                  <span className="ml-2 text-purple-600">
                    ({filteredFiles.length} file{filteredFiles.length !== 1 ? 's' : ''} found)
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
        {showSortOptions && (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 mb-6">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700">Sort Options</h4>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {/* Sort by Date */}
                <button
                  onClick={() => handleSortChange('date')}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                    sortBy === 'date'
                      ? 'bg-blue-50 border-blue-200 text-blue-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>📅</span>
                    <span className="text-sm font-medium">Date/Time</span>
                  </div>
                  {sortBy === 'date' && (
                    <span className="text-blue-600">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </button>

                {/* Sort by Size */}
                <button
                  onClick={() => handleSortChange('size')}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                    sortBy === 'size'
                      ? 'bg-blue-50 border-blue-200 text-blue-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>📏</span>
                    <span className="text-sm font-medium">Size</span>
                  </div>
                  {sortBy === 'size' && (
                    <span className="text-blue-600">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </button>

                {/* Sort by Filename */}
                <button
                  onClick={() => handleSortChange('filename')}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                    sortBy === 'filename'
                      ? 'bg-blue-50 border-blue-200 text-blue-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>🔤</span>
                    <span className="text-sm font-medium">Name</span>
                  </div>
                  {sortBy === 'filename' && (
                    <span className="text-blue-600">
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </button>
              </div>

              <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Current Sort:</span>
                  <span className="ml-2">
                    {sortBy === 'date' ? 'Date/Time' : sortBy === 'size' ? 'Size' : 'Name'} - {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
                  </span>
                </div>
                <Button
                  onClick={() => setShowSortOptions(false)}
                  variant="outline"
                  size="sm"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        )}

        {files.length === 0 ? (
          <div className="text-center py-12">
            <div className="mb-4">
              <svg className="w-16 h-16 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No files uploaded yet</h3>
            <p className="text-gray-600 mb-4">Upload some images to see them here</p>
            <Link to="/upload">
              <Button>Upload Files</Button>
            </Link>
          </div>
        ) : (
          <>
            {/* Controls */}
            <div className="bg-white rounded-lg shadow p-4 mb-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      checked={selectedFiles.size === currentFiles.length && currentFiles.length > 0}
                      onChange={handleSelectAll}
                    />
                    <span className="ml-2 text-sm text-gray-700">Select all on page</span>
                  </label>
                  <span className="text-sm text-gray-600">
                    {selectedFiles.size} selected
                  </span>
                </div>
                <Button
                  onClick={handleDeleteSelected}
                  disabled={selectedFiles.size === 0 || isDeleting}
                  variant="destructive"
                  size="sm"
                >
                  {isDeleting ? 'Deleting...' : `Delete Selected (${selectedFiles.size})`}
                </Button>
              </div>
            </div>

            {/* File Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 mb-8">
              {currentFiles.map((file) => (
                <div
                  key={file.filename}
                  className={`bg-white rounded-lg shadow-sm border transition-all duration-200 hover:shadow-md ${
                    selectedFiles.has(file.filename) 
                      ? 'ring-2 ring-blue-500 border-blue-200' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {/* Image Container with Overlay */}
                  <div className="relative aspect-square bg-gray-50 rounded-t-lg overflow-hidden">
                    {/* Checkbox - Top Left */}
                    <div className="absolute top-1.5 left-1.5 z-10">
                      <label className="cursor-pointer">
                        <input
                          type="checkbox"
                          className="sr-only"
                          checked={selectedFiles.has(file.filename)}
                          onChange={(e) => handleFileSelect(file.filename, e.target.checked)}
                        />
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${
                          selectedFiles.has(file.filename)
                            ? 'bg-blue-600 border-blue-600'
                            : 'bg-white border-gray-300 hover:border-gray-400'
                        }`}>
                          {selectedFiles.has(file.filename) && (
                            <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                      </label>
                    </div>

                    {/* Detect Objects Button - Bottom Right */}
                    <div className="absolute bottom-1.5 right-1.5 z-10">
                      <button
                        onClick={() => handleDetectObjects(file.filename)}
                        disabled={isDetecting}
                        className={`w-6 h-6 rounded-full shadow-lg flex items-center justify-center transition-all ${
                          isDetecting && selectedImage === file.filename
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-blue-600 hover:text-white'
                        }`}
                        title="Detect Objects"
                      >
                        {isDetecting && selectedImage === file.filename ? (
                          <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        )}
                      </button>
                    </div>

                    {/* Image */}
                    <img
                      src={getFileUrl(file.filename)}
                      alt={file.filename}
                      className="w-full h-full object-cover transition-transform duration-200 hover:scale-105 cursor-pointer"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextElementSibling.style.display = 'flex'
                      }}
                    />
                    <div className="hidden w-full h-full items-center justify-center text-gray-400 bg-gray-100">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>

                  {/* File Metadata */}
                  <div className="p-2">
                    {uploadsMetadata[file.filename] && uploadsMetadata[file.filename].original_filename ? (
                      <>
                        <h3 className="font-medium text-gray-900 text-xs mb-1 line-clamp-2" title={uploadsMetadata[file.filename].original_filename}>
                          {uploadsMetadata[file.filename].original_filename}
                        </h3>
                        <p className="text-xs text-gray-400 mb-1 truncate" title={`Stored as: ${file.filename}`}>
                          {file.filename}
                        </p>
                      </>
                    ) : (
                      <h3 className="font-medium text-gray-900 text-xs mb-1 line-clamp-2" title={file.filename}>
                        {file.filename}
                      </h3>
                    )}
                    <div className="space-y-0.5 text-xs text-gray-500 mb-2">
                      <div className="flex items-center justify-between">
                        <span>Size:</span>
                        <span className="font-medium">{formatFileSize(file.size)}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Modified:</span>
                        <span className="font-medium text-xs">{formatDate(file.modified)}</span>
                      </div>
                    </div>
                    
                    {/* Object Detection Metadata */}
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      {uploadsMetadata[file.filename] ? (
                        uploadsMetadata[file.filename].objects.length > 0 ? (
                          <div className="space-y-1">
                            <div className="text-xs text-gray-600 font-medium">
                              Objects ({uploadsMetadata[file.filename].objects.length}):
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {uploadsMetadata[file.filename].objects.slice(0, 3).map((obj, index) => {
                                const confidence = Math.round((obj.score || 0) * 100);
                                const getBadgeColor = (confidence) => {
                                  if (confidence >= 75) return 'bg-green-100 text-green-700 border-green-200';
                                  if (confidence >= 50) return 'bg-orange-100 text-orange-700 border-orange-200';
                                  return 'bg-red-100 text-red-700 border-red-200';
                                };
                                
                                return (
                                  <span 
                                    key={index} 
                                    className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border ${getBadgeColor(confidence)}`}
                                    title={`${obj.label} - ${confidence}% confidence`}
                                  >
                                    {obj.label}
                                  </span>
                                );
                              })}
                              {uploadsMetadata[file.filename].objects.length > 3 && (
                                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
                                  +{uploadsMetadata[file.filename].objects.length - 3}
                                </span>
                              )}
                            </div>
                          </div>
                        ) : (
                          <div className="text-xs text-gray-500 italic">No objects detected</div>
                        )
                      ) : (
                        <div className="text-xs text-gray-400 italic">
                          {isLoadingMetadata ? 'Loading...' : 'No metadata'}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 order-2 sm:order-1">
                  Showing {startIndex + 1} to {Math.min(endIndex, filteredFiles.length)} of {filteredFiles.length} results
                </div>
                
                <div className="flex items-center space-x-1 order-1 sm:order-2">
                  {/* Previous button */}
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Previous
                  </button>
                  
                  {/* Page numbers */}
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                      let pageNum
                      if (totalPages <= 5) {
                        pageNum = i + 1
                      } else if (currentPage <= 3) {
                        pageNum = i + 1
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i
                      } else {
                        pageNum = currentPage - 2 + i
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                  </div>
                  
                  {/* Next button */}
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 text-sm rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Confirm Deletion
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete {selectedFiles.size} selected file{selectedFiles.size !== 1 ? 's' : ''}? 
                This action cannot be undone.
              </p>
              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={cancelDelete}
                  disabled={isDeleting}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={confirmDelete}
                  disabled={isDeleting}
                >
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detection Results Modal */}
      {showDetectionModal && selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Object Detection Results - {selectedImage}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={closeDetectionModal}
                >
                  Close
                </Button>
              </div>

              {/* Detection Results */}
              {detectionResults ? (
                <div className="space-y-4">
                  {/* Results Summary */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">
                      Found {detectionResults.boxes?.length || 0} object{(detectionResults.boxes?.length || 0) !== 1 ? 's' : ''}
                    </p>
                  </div>

                  {/* Image with Detection Overlay */}
                  <div className="flex justify-center">
                    <div className="max-w-full">
                      <DetectionOverlay
                        imageUrl={getFileUrl(selectedImage)}
                        boxes={detectionResults.boxes || []}
                      />
                    </div>
                  </div>

                  {/* Detection Details */}
                  {detectionResults.boxes && detectionResults.boxes.length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Detected Objects:</h4>
                      <div className="flex flex-wrap gap-2">
                        {detectionResults.boxes.map((box, index) => {
                          const confidence = Math.round((box.score || 0) * 100);
                          const getBadgeColor = (confidence) => {
                            if (confidence >= 75) return 'bg-green-100 text-green-800 border-green-200';
                            if (confidence >= 50) return 'bg-orange-100 text-orange-800 border-orange-200';
                            return 'bg-red-100 text-red-800 border-red-200';
                          };
                          
                          return (
                            <span 
                              key={index} 
                              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getBadgeColor(confidence)}`}
                            >
                              {box.label} - {confidence}%
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Processing image...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadList