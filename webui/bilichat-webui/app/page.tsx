"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Moon, Sun, Shield, Code, ChevronDown, ChevronUp, Languages, LogOut } from "lucide-react"
import { ConfigEditor } from "@/components/config-editor"
import { I18nProvider, useI18n } from "@/lib/i18n"
import { useAuth } from "@/hooks/use-auth"
import { loginWithOTP, setToken } from "@/lib/api"

export default function HomePage() {
  return (
    <I18nProvider>
      <HomePageContent />
    </I18nProvider>
  )
}

function HomePageContent() {
  const { t, language, setLanguage } = useI18n()
  const { isAuthenticated, isLoading, logout, setIsAuthenticated } = useAuth()
  const [isDark, setIsDark] = useState(false)
  const [inputOTP, setInputOTP] = useState("")
  const [showSourceCode, setShowSourceCode] = useState(false)
  const [error, setError] = useState("")
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  useEffect(() => {
    // Apply theme
    if (isDark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [isDark])

  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputOTP.trim()) return

    setIsLoggingIn(true)
    setError("")

    try {
      const response = await loginWithOTP(inputOTP)

      if (response.success && response.access_token) {
        setToken(response.access_token)
        setIsAuthenticated(true)
      } else {
        setError(response.message || t("ui.auth.invalid_otp"))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("ui.auth.login_failed"))
    } finally {
      setIsLoggingIn(false)
    }
  }

  if (isLoading) {
    return (
      <div
        className={`min-h-screen flex items-center justify-center transition-colors duration-300 ${isDark ? "dark bg-gray-900" : "bg-gray-50"}`}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{t("ui.loading")}</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className={`min-h-screen transition-colors duration-300 ${isDark ? "dark bg-gray-900" : "bg-gray-50"}`}>
        <div className="container mx-auto px-4 py-8">
          {/* Theme Toggle */}
          <div className="flex justify-end mb-8">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsDark(!isDark)}
              className="rounded-full border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {isDark ? (
                <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              ) : (
                <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              )}
            </Button>
          </div>

          {/* Authentication Card */}
          <div className="flex items-center justify-center min-h-[60vh]">
            <Card className="w-full max-w-md">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                  <Shield className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle>{t("ui.auth.title")}</CardTitle>
                <CardDescription>{t("ui.auth.description")}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleOTPSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="otp">{t("ui.auth.enter_otp")}</Label>
                    <Input
                      id="otp"
                      type="text"
                      value={inputOTP}
                      onChange={(e) => setInputOTP(e.target.value)}
                      placeholder={t("ui.auth.otp_placeholder")}
                      className="text-center text-lg font-mono"
                      disabled={isLoggingIn}
                    />
                  </div>

                  {error && <div className="text-sm text-red-600 dark:text-red-400 text-center">{error}</div>}

                  <Button type="submit" className="w-full" disabled={isLoggingIn}>
                    {isLoggingIn ? t("ui.auth.logging_in") : t("ui.auth.authenticate")}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? "dark bg-gray-900" : "bg-gray-50"}`}>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t("ui.title")}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{t("ui.subtitle")}</p>
          </div>

          <div className="flex items-center gap-4">
            {/* Source Code Toggle */}
            <Button
              variant="outline"
              onClick={() => setShowSourceCode(!showSourceCode)}
              className="flex items-center gap-2 dark:text-white dark:border-gray-600"
            >
              <Code className="h-4 w-4" />
              {t("ui.source")}
              {showSourceCode ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>

            {/* Language Toggle */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setLanguage(language === "zh" ? "en" : "zh")}
              className="rounded-full border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
              title={t("ui.language")}
            >
              <Languages className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </Button>

            {/* Theme Toggle */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setIsDark(!isDark)}
              className="rounded-full border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {isDark ? (
                <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              ) : (
                <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              )}
            </Button>

            {/* Logout Button */}
            <Button
              variant="outline"
              size="icon"
              onClick={logout}
              className="rounded-full border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 bg-transparent"
              title={t("ui.logout")}
            >
              <LogOut className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </Button>
          </div>
        </div>

        {/* Configuration Editor */}
        <ConfigEditor showSourceCode={showSourceCode} />
      </div>
    </div>
  )
}
