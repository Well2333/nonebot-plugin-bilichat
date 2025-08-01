"use client"

import { useState, useEffect } from "react"
import { getConfig, setConfig, type Config } from "@/lib/api"

export function useConfig() {
  const [config, setConfigState] = useState<Config | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const configData = await getConfig()
      setConfigState(configData)
      setHasChanges(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load configuration")
    } finally {
      setIsLoading(false)
    }
  }

  const updateConfig = (path: string[], value: any) => {
    if (!config) return

    const newConfig = { ...config }
    let current: any = newConfig

    for (let i = 0; i < path.length - 1; i++) {
      current = current[path[i]]
    }

    current[path[path.length - 1]] = value
    setConfigState(newConfig)
    setHasChanges(true)
  }

  const saveConfig = async (): Promise<boolean> => {
    if (!config) return false

    try {
      setError(null)
      const savedConfig = await setConfig(config)
      setConfigState(savedConfig)
      setHasChanges(false)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save configuration")
      return false
    }
  }

  return {
    config,
    isLoading,
    error,
    hasChanges,
    updateConfig,
    saveConfig,
    reloadConfig: loadConfig,
  }
}
