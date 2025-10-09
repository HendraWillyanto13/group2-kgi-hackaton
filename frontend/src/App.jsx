import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Upload, MessageCircle, FolderOpen, FileText, FileSpreadsheet, BarChart3, Users, Settings, LogOut, User } from 'lucide-react'
import { Button } from './components/ui/button'
import { toast } from './hooks/use-toast'
import Layout from './components/Layout'
import UploadList from './pages/UploadList'
import ManageSource from './pages/ManageSource'
import UploadKnowledge from './pages/UploadKnowledge'
import ChatAsk from './pages/ChatAsk'
import './App.css'

function HomePage() {
  const handleUploadKnowledge = () => {
    toast.success('Navigating to Upload Knowledge...')
  }

  const handleAsk = () => {
    toast.success('Ask functionality activated...')
  }

  const handleAnalyzeData = () => {
    toast.success('Navigating to Data Analysis...')
  }

  const handleMaintainWearnessFormula = () => {
    toast.success('Navigating to Maintain Wearness Formula...')
  }

  const handleUserManagement = () => {
    toast.success('Navigating to User Management...')
  }

  const handleManageKnowledge = () => {
    toast.success('Navigating to Manage Knowledge...')
  }

  return (
    <div className="p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Main Action Buttons */}
          <div className="space-y-4 mb-8">
            <Link to="/chat" className="block">
              <Button 
                onClick={handleAsk}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <MessageCircle className="h-6 w-6" />
                Ask AI
              </Button>
            </Link>

            <Link to="/upload-knowledge" className="block">
              <Button 
                onClick={handleUploadKnowledge}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <FileSpreadsheet className="h-6 w-6" />
                Upload Knowledge
              </Button>
            </Link>
            
            <Link to="/analyze" className="block">
              <Button 
                onClick={handleAnalyzeData}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <BarChart3 className="h-6 w-6" />
                Analyze Data
              </Button>
            </Link>
            
            <Link to="/manage-knowledge" className="block">
              <Button 
                onClick={handleManageKnowledge}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <FolderOpen className="h-6 w-6" />
                Manage Knowledge
              </Button>
            </Link>

            <Link to="/maintain-wearness-formula" className="block">
              <Button 
                onClick={handleMaintainWearnessFormula}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <Settings className="h-6 w-6" />
                Maintain Wearness Formula
              </Button>
            </Link>

            <Link to="/user-management" className="block">
              <Button 
                onClick={handleUserManagement}
                className="komatsu-button w-full gap-2 text-lg px-6 py-4 h-auto"
              >
                <Users className="h-6 w-6" />
                User Management
              </Button>
            </Link>
          </div>

        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/files" element={<UploadList />} />
          <Route path="/manage-knowledge" element={<ManageSource />} />
          <Route path="/upload-knowledge" element={<UploadKnowledge />} />
          <Route path="/chat" element={<ChatAsk />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App