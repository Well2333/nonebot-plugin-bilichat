"use client"

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || ""

// 动态获取API路径 - 从当前页面路径推断
const getApiPath = (): string => {
  if (typeof window === "undefined") {
    // SSR环境下的默认值
    return "/bilichatwebui"
  }
  
  // 从当前页面路径推断API路径
  // 例如：如果页面在 /custom-path/ 下，API就在 /custom-path
  const pathname = window.location.pathname
  const pathSegments = pathname.split('/').filter(Boolean)
  
  if (pathSegments.length > 0) {
    return `/${pathSegments[0]}`
  }
  
  // 默认回退值
  return "/bilichatwebui"
}

// Types based on the OpenAPI schema
export interface OTPLoginRequest {
  code: string
}

export interface OTPLoginResponse {
  success: boolean
  access_token?: string | null
  token_type: string
  message: string
}

export interface Config {
  version: string
  webui: {
    enable: boolean
    api_path: string
    jwt_secret_key: string
  }
  nonebot: {
    block: boolean
    fallback: boolean
    enable_self: boolean
    only_self: boolean
    only_to_me: boolean
    command_to_me: boolean
    cmd_start: string
    cmd_add_sub: string[]
    cmd_remove_sub: string[]
    cmd_check_sub: string[]
    [key: string]: any
  }
  api: {
    request_api: Array<{
      api: string
      token: string
      weight: number
      enable: boolean
      note: string
    }>
    local_api_config: {
      enable: boolean
      api_path: string
      api_access_token: string
      api_sub_dynamic_limit: string
      api_sub_live_limit: string
    }
    browser_shot_quality: number
    api_health_check_interval: number
  }
  analyze: {
    video: boolean
    dynamic: boolean
    column: boolean
    cd_time: number
  }
  subs: {
    dynamic_interval: number
    live_interval: number
    push_delay: number
    users: Record<string, any>
  }
}

// Token management
export const getToken = (): string | null => {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

export const setToken = (token: string): void => {
  if (typeof window === "undefined") return
  localStorage.setItem("access_token", token)
}

export const removeToken = (): void => {
  if (typeof window === "undefined") return
  localStorage.removeItem("access_token")
}

// API client with authentication
const apiClient = async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
  const token = getToken()
  const headers = new Headers(options.headers)
  headers.set("Content-Type", "application/json")

  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  // 动态获取API路径
  const apiPath = getApiPath()
  const response = await fetch(`${API_BASE_URL}${apiPath}${endpoint}`, {
    ...options,
    headers,
  })

  // Handle 401 unauthorized
  if (response.status === 401) {
    removeToken()
    window.location.reload()
  }

  return response
}

// API functions
export const loginWithOTP = async (code: string): Promise<OTPLoginResponse> => {
  const response = await apiClient("/auth/login", {
    method: "POST",
    body: JSON.stringify({ code }),
  })

  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`)
  }

  return response.json()
}

export const getCurrentUser = async (): Promise<any> => {
  const response = await apiClient("/auth/me")

  if (!response.ok) {
    throw new Error(`Failed to get user info: ${response.statusText}`)
  }

  return response.json()
}

export const getConfig = async (): Promise<Config> => {
  const response = await apiClient("/config")

  if (!response.ok) {
    throw new Error(`Failed to get config: ${response.statusText}`)
  }

  return response.json()
}

export const setConfig = async (config: Config): Promise<Config> => {
  const response = await apiClient("/config", {
    method: "POST",
    body: JSON.stringify(config),
  })

  if (!response.ok) {
    throw new Error(`Failed to save config: ${response.statusText}`)
  }

  return response.json()
}

export const getConfigSchema = async (): Promise<any> => {
  const response = await apiClient("/config/schema")

  if (!response.ok) {
    throw new Error(`Failed to get config schema: ${response.statusText}`)
  }

  return response.json()
}
