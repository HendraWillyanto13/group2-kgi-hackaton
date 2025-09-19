import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Upload } from 'lucide-react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Progress } from './components/ui/progress'
import { Toaster } from './components/ui/toaster'
import { toast } from './hooks/use-toast'
import UploadPage from './pages/UploadPage'
import UploadList from './pages/UploadList'

function HomePage() {
  const [progress, setProgress] = useState(33)
  const [inputValue, setInputValue] = useState('')

  const handleProgressUpdate = () => {
    const newProgress = progress >= 100 ? 0 : progress + 10
    setProgress(newProgress)
    toast.success(`Progress updated to ${newProgress}%`)
  }

  const handleInputSubmit = () => {
    if (inputValue.trim()) {
      toast.success(`Input submitted: ${inputValue}`)
      setInputValue('')
    } else {
      toast.error('Please enter some text')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 text-center">
            Vite + React + Tailwind
          </h1>
          <p className="text-gray-600 text-center mb-8">
            shadcn/ui Components Demo
          </p>
          
          {/* Navigation */}
          <div className="mb-8 text-center">
            <Link to="/upload">
              <Button className="gap-2 text-lg px-6 py-3">
                <Upload className="h-5 w-5" />
                Upload Images
              </Button>
            </Link>
          </div>
          
          {/* Progress Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Progress Component</h2>
            <div className="space-y-4">
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-gray-600">Progress: {progress}%</p>
              <Button onClick={handleProgressUpdate} className="bg-green-600 hover:bg-green-700">
                Update Progress
              </Button>
            </div>
          </div>
          
          {/* Input Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Input Component</h2>
            <div className="space-y-4">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter some text..."
                className="w-full"
              />
              <Button 
                onClick={handleInputSubmit}
                variant="outline" 
                className="w-full"
              >
                Submit Input
              </Button>
            </div>
          </div>
          
          {/* Button Variants Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Button Variants</h2>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => toast.success('Default clicked!')}>Default</Button>
              <Button variant="secondary" onClick={() => toast.success('Secondary clicked!')}>
                Secondary
              </Button>
              <Button variant="outline" onClick={() => toast.success('Outline clicked!')}>
                Outline
              </Button>
              <Button variant="ghost" onClick={() => toast.success('Ghost clicked!')}>
                Ghost
              </Button>
              <Button variant="destructive" onClick={() => toast.error('Destructive clicked!')}>
                Destructive
              </Button>
            </div>
          </div>

          <div className="text-center text-sm text-gray-500">
            Edit <code className="bg-gray-100 px-2 py-1 rounded">src/App.jsx</code> and save to test HMR
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
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
}

export default App
