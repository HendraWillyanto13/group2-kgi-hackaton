import React, { useState } from 'react';
import { LogOut, User } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import { Toaster } from '../components/ui/toaster';

const Layout = ({ children }) => {
  // User state - for demo purposes, using static user data
  const [user] = useState({
    name: 'Dwi Fitriansyah',
    role: 'KUI - Marketing',
    email: 'dwi.fitriansyah@global.komatsu'
  });

  const handleLogout = () => {
    toast.success('Logging out...');
    // Here you would typically clear user session, tokens, etc.
    // For demo purposes, just showing a toast
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Sticky Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm border-b border-gray-200 px-8 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          {/* Logo and Title - Left Side */}
          <div className="flex items-center space-x-4">
            <img 
              src="/komatsu-logo.png" 
              alt="Komatsu Logo" 
              className="h-10 w-auto object-contain"
            />
            <div>
              <h1 className="text-sm sm:text-base md:text-lg lg:text-xl font-bold text-gray-900">
                Undercarriage Monitoring and Diagnostics Apps
              </h1>        
            </div>
          </div>

          {/* User and Logout - Right Side */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-600" />
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">{user.name}</div>
                <div className="text-xs text-gray-500">{user.role}</div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>

      {/* Sticky Footer */}
      <footer className="sticky bottom-0 z-50 bg-white border-t border-gray-200 px-8 py-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-1">
            <div className="text-sm text-gray-500">
              Version 1.0.0
            </div>
            <div className="text-xs text-gray-400">
              © 2025 PT Komatsu Undercarriage Indonesia. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

      {/* Custom positioned Toaster */}
      <div className="fixed top-20 right-4 z-40">
        <Toaster />
      </div>
    </div>
  );
};

export default Layout;