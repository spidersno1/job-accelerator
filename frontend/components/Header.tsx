'use client'

import React from 'react'
import { useState } from 'react'
import Link from 'next/link'
import { Menu, X, User, LogOut } from 'lucide-react'
import { useAuth } from './AuthProvider'

export default function Header() {
  const { isLoggedIn, setIsLoggedIn } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">
              程序员求职加速器
            </h1>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {isLoggedIn ? (
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
                >
                  <LogOut size={16} />
                  <span>退出</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link href="/login" className="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-4 py-2 rounded-md hover:from-blue-500 hover:to-blue-600 transition-all duration-300">
                  登录
                </Link>
                <Link href="/register" className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-md hover:from-blue-600 hover:to-blue-700 transition-all duration-300 ml-2">
                  注册
                </Link>
              </div>
            )}
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {isLoggedIn ? (
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 block px-3 py-2"
                >
                  <LogOut size={16} />
                  <span>退出</span>
                </button>
              ) : (
                <>
                  <Link href="/login" className="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-4 py-2 rounded-md hover:from-blue-500 hover:to-blue-600 transition-all duration-300 block w-full text-left mb-2">
                  登录
                </Link>
                <Link href="/register" className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-2 rounded-md hover:from-blue-600 hover:to-blue-700 transition-all duration-300 block w-full text-left">
                  注册
                </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
