import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Upload, MessageCircle, FolderOpen, FileText } from 'lucide-react'
import { Button } from './components/ui/button'
import { Toaster } from './components/ui/toaster'
import { toast } from './hooks/use-toast'
import UploadPage from './pages/UploadPage'
import UploadList from './pages/UploadList'
import ManageSource from './pages/ManageSource'
import UploadDocument from './pages/UploadDocument'
import ChatAsk from './pages/ChatAsk'

function HomePage() {
  const handleUploadImage = () => {
    toast.success('Navigating to Upload Image...')
  }

  const handleUploadDocument = () => {
    toast.success('Navigating to Upload Document...')
  }

  const handleAsk = () => {
    toast.success('Ask functionality activated...')
  }

  const handleManageSource = () => {
    toast.success('Navigating to Manage Source...')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 text-center">
            KGI Hackaton - Group 2
          </h1>
          <p className="text-gray-600 text-center mb-8">
            Upload, Ask, and Manage your documents
          </p>
          
          {/* Main Action Buttons */}
          <div className="space-y-4 mb-8">
            <Link to="/upload" className="block">
              <Button 
                onClick={handleUploadImage}
                className="w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <Upload className="h-6 w-6" />
                Upload Image
              </Button>
            </Link>
            
            <Link to="/upload-document" className="block">
              <Button 
                onClick={handleUploadDocument}
                className="w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <FileText className="h-6 w-6" />
                Upload Document
              </Button>
            </Link>
            
            <Link to="/chat" className="block">
              <Button 
                onClick={handleAsk}
                className="w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <MessageCircle className="h-6 w-6" />
                Ask
              </Button>
            </Link>
            
            <Link to="/manage-source" className="block">
              <Button 
                onClick={handleManageSource}
                className="w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <FolderOpen className="h-6 w-6" />
                Manage Source
              </Button>
            </Link>
          </div>

          <div className="text-center text-sm text-gray-500">
            Choose an action above to get started
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/files" element={<UploadList />} />
        <Route path="/manage-source" element={<ManageSource />} />
        <Route path="/upload-document" element={<UploadDocument />} />
        <Route path="/chat" element={<ChatAsk />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
