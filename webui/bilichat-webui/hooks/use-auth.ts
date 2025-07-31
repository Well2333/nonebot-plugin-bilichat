"use client"

import { useState, useEffect } from "react"
import { getToken, removeToken, getCurrentUser } from "@/lib/api"

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken()

      if (!token) {
        setIsAuthenticated(false)
        setIsLoading(false)
        return
      }

      try {
        const userInfo = await getCurrentUser()
        setUser(userInfo)
        setIsAuthenticated(true)
      } catch (error) {
        console.error("Auth check failed:", error)
        removeToken()
        setIsAuthenticated(false)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const logout = () => {
    removeToken()
    setIsAuthenticated(false)
    setUser(null)
  }

  return {
    isAuthenticated,
    isLoading,
    user,
    logout,
    setIsAuthenticated,
  }
}
