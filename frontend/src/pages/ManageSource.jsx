import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  Search, 
  Filter, 
  ChevronUp, 
  ChevronDown, 
  Trash2, 
  Eye,
  Check,
  Square
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { toast } from '../hooks/use-toast'
import { getDocuments, deleteDocuments, getPDFUrl } from '../lib/api'

const ManageSource = () => {
  const [documents, setDocuments] = useState([])
  const [filteredDocuments, setFilteredDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDocuments, setSelectedDocuments] = useState(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [sizeFilter, setSizeFilter] = useState('')
  const [dateFilter, setDateFilter] = useState('')

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    filterAndSortDocuments()
  }, [documents, searchTerm, sortConfig, sizeFilter, dateFilter])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const response = await getDocuments()
      const processedDocs = response.pdfs.map((doc, index) => ({
        id: doc.stored_filename || `doc-${index}`,
        name: doc.original_filename,
        storedFilename: doc.stored_filename,
        uploadDate: new Date(doc.processed_time || doc.uploaded_time),
        size: doc.file_size || 0,
        fileHash: doc.file_hash, // Use file_hash for deletion
      }))
      setDocuments(processedDocs)
    } catch (error) {
      console.error('Error loading documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const filterAndSortDocuments = () => {
    let filtered = [...documents]

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply size filter
    if (sizeFilter) {
      const sizeValue = parseFloat(sizeFilter)
      if (!isNaN(sizeValue)) {
        filtered = filtered.filter(doc => {
          const docSizeMB = doc.size / (1024 * 1024)
          return docSizeMB >= sizeValue
        })
      }
    }

    // Apply date filter
    if (dateFilter) {
      const filterDate = new Date(dateFilter)
      filtered = filtered.filter(doc => 
        doc.uploadDate >= filterDate
      )
    }

    // Apply sorting
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        let aValue = a[sortConfig.key]
        let bValue = b[sortConfig.key]

        if (sortConfig.key === 'uploadDate') {
          aValue = aValue.getTime()
          bValue = bValue.getTime()
        } else if (sortConfig.key === 'size') {
          aValue = aValue || 0
          bValue = bValue || 0
        } else if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase()
          bValue = bValue.toLowerCase()
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1
        }
        return 0
      })
    }

    setFilteredDocuments(filtered)
  }

  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const handleSelectDocument = (id) => {
    const newSelected = new Set(selectedDocuments)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedDocuments(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedDocuments.size === filteredDocuments.length) {
      setSelectedDocuments(new Set())
    } else {
      setSelectedDocuments(new Set(filteredDocuments.map(doc => doc.id)))
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedDocuments.size === 0) {
      toast.error('No documents selected')
      return
    }

    try {
      const selectedFileHashes = Array.from(selectedDocuments).map(id => {
        const doc = documents.find(d => d.id === id)
        return doc.fileHash
      })

      const result = await deleteDocuments(selectedFileHashes)
      
      if (result.total_deleted > 0) {
        toast.success(`Delete Successfully - ${result.total_deleted} files deleted`)
      } else {
        toast.error('No files were deleted')
      }
      
      setSelectedDocuments(new Set())
      await loadDocuments()
    } catch (error) {
      console.error('Error deleting documents:', error)
      toast.error('Delete Failed')
    } finally {
      setShowDeleteConfirm(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const handlePreviewDocument = (doc) => {
    const url = getPDFUrl(doc.storedFilename)
    window.open(url, '_blank')
  }

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) {
      return <ChevronUp className="h-4 w-4 text-gray-400" />
    }
    return sortConfig.direction === 'asc' 
      ? <ChevronUp className="h-4 w-4 text-blue-600" />
      : <ChevronDown className="h-4 w-4 text-blue-600" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="text-center">Loading documents...</div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="outline" className="gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Back to Home
                </Button>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Manage Source</h1>
            </div>
            <div className="text-sm text-gray-600">
              Total Documents: {filteredDocuments.length}
            </div>
          </div>

          {/* Filters and Search */}
          <div className="mb-6 space-y-4">
            <div className="flex gap-4 items-center flex-wrap">
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search by name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <input
                  type="date"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Min Size (MB):</span>
                <input
                  type="number"
                  placeholder="0"
                  value={sizeFilter}
                  onChange={(e) => setSizeFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-24"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                onClick={() => setShowDeleteConfirm(true)}
                disabled={selectedDocuments.size === 0}
                className="gap-2 bg-red-600 hover:bg-red-700"
              >
                <Trash2 className="h-4 w-4" />
                Delete Selected ({selectedDocuments.size})
              </Button>
            </div>
          </div>

          {/* Documents Table */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border border-gray-300 p-3 text-left">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleSelectAll}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        {selectedDocuments.size === filteredDocuments.length && filteredDocuments.length > 0
                          ? <Check className="h-4 w-4 text-blue-600" />
                          : <Square className="h-4 w-4 text-gray-500" />
                        }
                      </button>
                      Select All
                    </div>
                  </th>
                  <th className="border border-gray-300 p-3 text-left">
                    <button
                      onClick={() => handleSort('name')}
                      className="flex items-center gap-2 hover:text-blue-600"
                    >
                      Name
                      {getSortIcon('name')}
                    </button>
                  </th>
                  <th className="border border-gray-300 p-3 text-left">
                    <button
                      onClick={() => handleSort('uploadDate')}
                      className="flex items-center gap-2 hover:text-blue-600"
                    >
                      Upload Date
                      {getSortIcon('uploadDate')}
                    </button>
                  </th>
                  <th className="border border-gray-300 p-3 text-left">
                    <button
                      onClick={() => handleSort('size')}
                      className="flex items-center gap-2 hover:text-blue-600"
                    >
                      Size
                      {getSortIcon('size')}
                    </button>
                  </th>
                  <th className="border border-gray-300 p-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="border border-gray-300 p-3">
                      <button
                        onClick={() => handleSelectDocument(doc.id)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        {selectedDocuments.has(doc.id)
                          ? <Check className="h-4 w-4 text-blue-600" />
                          : <Square className="h-4 w-4 text-gray-500" />
                        }
                      </button>
                    </td>
                    <td className="border border-gray-300 p-3">
                      <div className="font-medium text-gray-900">{doc.name}</div>
                    </td>
                    <td className="border border-gray-300 p-3">
                      <div className="text-gray-600">{formatDate(doc.uploadDate)}</div>
                    </td>
                    <td className="border border-gray-300 p-3">
                      <div className="text-gray-600">{formatFileSize(doc.size)}</div>
                    </td>
                    <td className="border border-gray-300 p-3">
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handlePreviewDocument(doc)}
                          size="sm"
                          className="gap-1"
                        >
                          <Eye className="h-3 w-3" />
                          Preview
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredDocuments.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No documents found.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete {selectedDocuments.size} selected document(s)? 
              This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button
                onClick={() => setShowDeleteConfirm(false)}
                variant="outline"
              >
                Cancel
              </Button>
              <Button
                onClick={handleDeleteSelected}
                className="bg-red-600 hover:bg-red-700"
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ManageSource