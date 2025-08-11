"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Save, Settings, Bot, Database, Bell, Plus, Trash2, Code, AlertCircle, Loader2, Edit3, User, Users } from "lucide-react"
import { useI18n } from "@/lib/i18n"
import { ConfigField } from "./config-field"
import { useConfig } from "@/hooks/use-config"
import { useState } from "react"

interface ConfigEditorProps {
  showSourceCode: boolean
}

interface UserConfig {
  info?: {
    self_id?: string
    adapter?: string
    scope?: string
    scene?: {
      id?: string
      type?: number
      name?: string
      avatar?: string | null
      parent?: unknown
    }
    user?: {
      id?: string
      name?: string | null
      nick?: string | null
      avatar?: string
      gender?: string
    }
    member?: unknown
    operator?: unknown
    platform?: unknown
  }
  id?: string
  subscribes?: Array<{
    uid: number
    uname: string
    nickname: string
    note: string
    dynamic: Record<string, "PUSH" | "IGNORE">
    live: "PUSH" | "IGNORE"
  }>
}

interface SubscribeConfig {
  uid: number
  uname: string
  nickname: string
  note: string
  dynamic: Record<string, "PUSH" | "IGNORE">
  live: "PUSH" | "IGNORE"
}

// 动态类型配置选项
const DYNAMIC_TYPES = [
  "DYNAMIC_TYPE_AD",
  "DYNAMIC_TYPE_APPLET", 
  "DYNAMIC_TYPE_ARTICLE",
  "DYNAMIC_TYPE_AV",
  "DYNAMIC_TYPE_BANNER",
  "DYNAMIC_TYPE_COMMON_SQUARE",
  "DYNAMIC_TYPE_COMMON_VERTICAL",
  "DYNAMIC_TYPE_COURSES",
  "DYNAMIC_TYPE_COURSES_BATCH",
  "DYNAMIC_TYPE_COURSES_SEASON",
  "DYNAMIC_TYPE_DRAW",
  "DYNAMIC_TYPE_FORWARD",
  "DYNAMIC_TYPE_LIVE",
  "DYNAMIC_TYPE_LIVE_RCMD",
  "DYNAMIC_TYPE_MEDIALIST",
  "DYNAMIC_TYPE_MUSIC",
  "DYNAMIC_TYPE_NONE",
  "DYNAMIC_TYPE_PGC",
  "DYNAMIC_TYPE_SUBSCRIPTION",
  "DYNAMIC_TYPE_SUBSCRIPTION_NEW",
  "DYNAMIC_TYPE_UGC_SEASON",
  "DYNAMIC_TYPE_WORD"
] as const

interface UserConfigEditorProps {
  userId: string
  userConfig: UserConfig
  onConfigChange: (newConfig: UserConfig) => void
  onDeleteUser: (userId: string) => void
}

interface EnhancedSubscribeEditorProps {
  subscribe: SubscribeConfig
  onSubscribeChange: (newSubscribe: SubscribeConfig) => void
  onDeleteSubscribe: () => void
  onSetAllDynamicTypes: (value: "PUSH" | "IGNORE") => void
  onSetDefaultDynamicTypes: () => void
}



function EnhancedSubscribeEditor({ 
  subscribe, 
  onSubscribeChange, 
  onDeleteSubscribe, 
  onSetAllDynamicTypes, 
  onSetDefaultDynamicTypes 
}: EnhancedSubscribeEditorProps) {
  const { t } = useI18n()
  const [isDynamicTypesExpanded, setIsDynamicTypesExpanded] = useState(false)

  const updateField = (field: keyof SubscribeConfig, value: unknown) => {
    onSubscribeChange({
      ...subscribe,
      [field]: value
    })
  }

  const updateDynamicType = (type: string, value: "PUSH" | "IGNORE") => {
    onSubscribeChange({
      ...subscribe,
      dynamic: {
        ...subscribe.dynamic,
        [type]: value
      }
    })
  }

  // 计算动态推送的统计信息
  const dynamicStats = DYNAMIC_TYPES.reduce((stats, type) => {
    const value = subscribe.dynamic[type]
    if (value === "PUSH") stats.push++
    else if (value === "IGNORE") stats.ignore++
    return stats
  }, { push: 0, ignore: 0 })

  return (
    <div className="border rounded-lg p-4 bg-white dark:bg-gray-900 space-y-4">
      {/* 订阅基本信息 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-blue-600" />
            <span className="font-medium">{subscribe.uname || t("ui.unknown_user")}</span>
            <Badge variant="outline" className="text-xs">UID: {subscribe.uid}</Badge>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onDeleteSubscribe}
            className="flex items-center gap-1 text-xs text-red-600 hover:text-red-700"
          >
            <Trash2 className="h-3 w-3" />
            {t("ui.delete")}
          </Button>
        </div>
      </div>

      {/* 基本配置 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor={`uid-${subscribe.uid}`} className="text-sm font-medium">
            {t("ui.subscribe.uid")}
          </Label>
          <Input
            id={`uid-${subscribe.uid}`}
            type="number"
            value={subscribe.uid}
            onChange={(e) => updateField("uid", Number(e.target.value))}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor={`uname-${subscribe.uid}`} className="text-sm font-medium">
            {t("ui.subscribe.uname")}
          </Label>
          <Input
            id={`uname-${subscribe.uid}`}
            value={subscribe.uname}
            onChange={(e) => updateField("uname", e.target.value)}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor={`nickname-${subscribe.uid}`} className="text-sm font-medium">
            {t("ui.subscribe.nickname")}
          </Label>
          <Input
            id={`nickname-${subscribe.uid}`}
            value={subscribe.nickname}
            onChange={(e) => updateField("nickname", e.target.value)}
            placeholder={t("ui.optional")}
            className="mt-1"
          />
        </div>
        <div>
          <Label htmlFor={`note-${subscribe.uid}`} className="text-sm font-medium">
            {t("ui.subscribe.note")}
          </Label>
          <Input
            id={`note-${subscribe.uid}`}
            value={subscribe.note}
            onChange={(e) => updateField("note", e.target.value)}
            placeholder={t("ui.optional")}
            className="mt-1"
          />
        </div>
      </div>

      {/* 直播配置 */}
      <div>
        <Label className="text-sm font-medium">{t("ui.subscribe.live")}</Label>
        <div className="flex items-center justify-between text-sm border rounded p-3 mt-2 bg-gray-50 dark:bg-gray-800">
          <span className="text-gray-700 dark:text-gray-300">{t("ui.subscribe.live_notification")}</span>
          <div className="flex gap-2">
            <Button
              variant={subscribe.live === "PUSH" ? "default" : "outline"}
              size="sm"
              onClick={() => updateField("live", "PUSH")}
              className="h-7 px-3 text-xs"
            >
              {t("ui.push")}
            </Button>
            <Button
              variant={subscribe.live === "IGNORE" ? "default" : "outline"}
              size="sm"
              onClick={() => updateField("live", "IGNORE")}
              className="h-7 px-3 text-xs"
            >
              {t("ui.ignore")}
            </Button>
          </div>
        </div>
      </div>

      {/* 动态配置 */}
      <div>
        <Label className="text-sm font-medium">{t("ui.subscribe.dynamic")}</Label>
        <div className="border rounded p-3 mt-2 bg-gray-50 dark:bg-gray-800 space-y-3">
          {/* 动态推送总览和控制按钮 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {t("ui.subscribe.dynamic_notification")}
              </span>
              <Badge variant="secondary" className="text-xs">
                {dynamicStats.push} {t("ui.push")} / {dynamicStats.ignore} {t("ui.ignore")}
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onSetAllDynamicTypes("PUSH")}
                className="h-7 px-2 text-xs"
              >
                {t("ui.enable_all")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onSetAllDynamicTypes("IGNORE")}
                className="h-7 px-2 text-xs"
              >
                {t("ui.disable_all")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onSetDefaultDynamicTypes}
                className="h-7 px-2 text-xs"
              >
                {t("ui.default")}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsDynamicTypesExpanded(!isDynamicTypesExpanded)}
                className="h-7 px-2 text-xs"
              >
                <Edit3 className="h-3 w-3 mr-1" />
                {isDynamicTypesExpanded ? t("ui.collapse") : t("ui.expand")}
              </Button>
            </div>
          </div>

          {/* 详细动态类型配置 */}
          {isDynamicTypesExpanded && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pt-2 border-t">
              {DYNAMIC_TYPES.map((type) => (
                <div key={type} className="flex items-center justify-between text-xs border rounded p-2 bg-white dark:bg-gray-900">
                  <span className="text-gray-600 dark:text-gray-300 truncate mr-2">
                    {type.replace("DYNAMIC_TYPE_", "")}
                  </span>
                  <div className="flex gap-1">
                    <Button
                      variant={subscribe.dynamic[type] === "PUSH" ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateDynamicType(type, "PUSH")}
                      className="h-5 px-1 text-xs"
                    >
                      {t("ui.push")}
                    </Button>
                    <Button
                      variant={subscribe.dynamic[type] === "IGNORE" ? "default" : "outline"}
                      size="sm"
                      onClick={() => updateDynamicType(type, "IGNORE")}
                      className="h-5 px-1 text-xs"
                    >
                      {t("ui.ignore")}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function UserConfigEditor({ userId, userConfig, onConfigChange, onDeleteUser }: UserConfigEditorProps) {
  const { t } = useI18n()

  const addNewSubscribe = () => {
    const defaultDynamic: Record<string, "PUSH" | "IGNORE"> = {
      "DYNAMIC_TYPE_AD": "IGNORE",
      "DYNAMIC_TYPE_APPLET": "PUSH",
      "DYNAMIC_TYPE_ARTICLE": "PUSH",
      "DYNAMIC_TYPE_AV": "PUSH",
      "DYNAMIC_TYPE_BANNER": "IGNORE",
      "DYNAMIC_TYPE_COMMON_SQUARE": "PUSH",
      "DYNAMIC_TYPE_COMMON_VERTICAL": "PUSH",
      "DYNAMIC_TYPE_COURSES": "PUSH",
      "DYNAMIC_TYPE_COURSES_BATCH": "PUSH",
      "DYNAMIC_TYPE_COURSES_SEASON": "PUSH",
      "DYNAMIC_TYPE_DRAW": "PUSH",
      "DYNAMIC_TYPE_FORWARD": "PUSH",
      "DYNAMIC_TYPE_LIVE": "IGNORE",
      "DYNAMIC_TYPE_LIVE_RCMD": "IGNORE",
      "DYNAMIC_TYPE_MEDIALIST": "PUSH",
      "DYNAMIC_TYPE_MUSIC": "PUSH",
      "DYNAMIC_TYPE_NONE": "PUSH",
      "DYNAMIC_TYPE_PGC": "PUSH",
      "DYNAMIC_TYPE_SUBSCRIPTION": "PUSH",
      "DYNAMIC_TYPE_SUBSCRIPTION_NEW": "PUSH",
      "DYNAMIC_TYPE_UGC_SEASON": "PUSH",
      "DYNAMIC_TYPE_WORD": "PUSH"
    }

    const newSubscribe: SubscribeConfig = {
      uid: 0,
      uname: "",
      nickname: "",
      note: "",
      dynamic: defaultDynamic,
      live: "PUSH"
    }

    const newConfig = {
      ...userConfig,
      subscribes: [...(userConfig.subscribes || []), newSubscribe]
    }
    onConfigChange(newConfig)
  }

  const updateSubscribe = (index: number, newSubscribe: SubscribeConfig) => {
    const newSubscribes = [...(userConfig.subscribes || [])]
    newSubscribes[index] = newSubscribe
    onConfigChange({
      ...userConfig,
      subscribes: newSubscribes
    })
  }

  const deleteSubscribe = (index: number) => {
    const newSubscribes = (userConfig.subscribes || []).filter((_, i) => i !== index)
    onConfigChange({
      ...userConfig,
      subscribes: newSubscribes
    })
  }

  // 批量操作函数
  const setAllDynamicTypes = (subscribeIndex: number, value: "PUSH" | "IGNORE") => {
    const newSubscribes = [...(userConfig.subscribes || [])]
    const newDynamic: Record<string, "PUSH" | "IGNORE"> = {}
    DYNAMIC_TYPES.forEach(type => {
      newDynamic[type] = value
    })
    newSubscribes[subscribeIndex] = {
      ...newSubscribes[subscribeIndex],
      dynamic: newDynamic
    }
    onConfigChange({
      ...userConfig,
      subscribes: newSubscribes
    })
  }

  const setDefaultDynamicTypes = (subscribeIndex: number) => {
    const newSubscribes = [...(userConfig.subscribes || [])]
    const defaultDynamic: Record<string, "PUSH" | "IGNORE"> = {
      "DYNAMIC_TYPE_AD": "IGNORE",
      "DYNAMIC_TYPE_APPLET": "PUSH",
      "DYNAMIC_TYPE_ARTICLE": "PUSH",
      "DYNAMIC_TYPE_AV": "PUSH",
      "DYNAMIC_TYPE_BANNER": "IGNORE",
      "DYNAMIC_TYPE_COMMON_SQUARE": "PUSH",
      "DYNAMIC_TYPE_COMMON_VERTICAL": "PUSH",
      "DYNAMIC_TYPE_COURSES": "PUSH",
      "DYNAMIC_TYPE_COURSES_BATCH": "PUSH",
      "DYNAMIC_TYPE_COURSES_SEASON": "PUSH",
      "DYNAMIC_TYPE_DRAW": "PUSH",
      "DYNAMIC_TYPE_FORWARD": "PUSH",
      "DYNAMIC_TYPE_LIVE": "IGNORE",
      "DYNAMIC_TYPE_LIVE_RCMD": "IGNORE",
      "DYNAMIC_TYPE_MEDIALIST": "PUSH",
      "DYNAMIC_TYPE_MUSIC": "PUSH",
      "DYNAMIC_TYPE_NONE": "PUSH",
      "DYNAMIC_TYPE_PGC": "PUSH",
      "DYNAMIC_TYPE_SUBSCRIPTION": "PUSH",
      "DYNAMIC_TYPE_SUBSCRIPTION_NEW": "PUSH",
      "DYNAMIC_TYPE_UGC_SEASON": "PUSH",
      "DYNAMIC_TYPE_WORD": "PUSH"
    }
    newSubscribes[subscribeIndex] = {
      ...newSubscribes[subscribeIndex],
      dynamic: defaultDynamic
    }
    onConfigChange({
      ...userConfig,
      subscribes: newSubscribes
    })
  }

  return (
    <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800/50 space-y-4">
      {/* 用户头部信息 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-blue-600" />
            <Label className="font-medium text-sm">{t("ui.user")} {userId}</Label>
            <Badge variant="outline" className="text-xs">
              {userConfig?.info?.adapter || t("ui.unknown_adapter")}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {userConfig.subscribes?.length || 0} {t("ui.subscriptions")}
            </Badge>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDeleteUser(userId)}
            className="flex items-center gap-1 text-xs text-red-600 hover:text-red-700"
          >
            <Trash2 className="h-3 w-3" />
            {t("ui.delete_user")}
          </Button>
        </div>
      </div>

      {/* 用户基本信息显示 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        {userConfig?.info && (
          <>
            <div>
              <span className="text-gray-500">{t("ui.adapter")}:</span>
              <div className="font-medium">{userConfig.info.adapter}</div>
            </div>
            <div>
              <span className="text-gray-500">{t("ui.scene")}:</span>
              <div className="font-medium">{userConfig.info.scene?.name || userConfig.info.scene?.id}</div>
            </div>
            <div>
              <span className="text-gray-500">{t("ui.user")}:</span>
              <div className="font-medium">{userConfig.info.user?.name || userConfig.info.user?.id}</div>
            </div>
            <div>
              <span className="text-gray-500">Self ID:</span>
              <div className="font-medium">{userConfig.info.self_id}</div>
            </div>
          </>
        )}
      </div>

      {/* 订阅管理 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">{t("ui.subscriptions")}</Label>
          <Button
            variant="outline"
            size="sm"
            onClick={addNewSubscribe}
            className="flex items-center gap-1 text-xs"
          >
            <Plus className="h-3 w-3" />
            {t("ui.add_subscription")}
          </Button>
        </div>

        {/* 订阅列表 */}
        <div className="space-y-3">
          {userConfig.subscribes?.length === 0 || !userConfig.subscribes ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">{t("ui.no_subscriptions")}</p>
            </div>
          ) : (
            userConfig.subscribes.map((subscribe, index) => (
              <EnhancedSubscribeEditor
                key={`${subscribe.uid}-${index}`}
                subscribe={subscribe}
                onSubscribeChange={(newSubscribe) => updateSubscribe(index, newSubscribe)}
                onDeleteSubscribe={() => deleteSubscribe(index)}
                onSetAllDynamicTypes={(value) => setAllDynamicTypes(index, value)}
                onSetDefaultDynamicTypes={() => setDefaultDynamicTypes(index)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export function ConfigEditor({ showSourceCode }: ConfigEditorProps) {
  const { t } = useI18n()
  const { config, isLoading, error, hasChanges, updateConfig, saveConfig } = useConfig()

  const addApiEndpoint = () => {
    if (!config) return

    const newEndpoint = {
      api: "",
      token: "",
      weight: 1,
      enable: true,
      note: "",
    }
    const newApis = [...config.api.request_api, newEndpoint]
    updateConfig(["api", "request_api"], newApis)
  }

  const removeApiEndpoint = (index: number) => {
    if (!config) return

    const newApis = config.api.request_api.filter((_, i) => i !== index)
    updateConfig(["api", "request_api"], newApis)
  }

  const updateApiEndpoint = (index: number, field: string, value: string | number | boolean) => {
    if (!config) return

    const newApis = [...config.api.request_api]
    newApis[index] = { ...newApis[index], [field]: value }
    updateConfig(["api", "request_api"], newApis)
  }

  const handleSave = async () => {
    const success = await saveConfig()
    if (success) {
      // Show success message - you could use a toast library here
      alert(t("ui.save_success"))
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">{t("ui.loading_config")}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
            <AlertCircle className="h-5 w-5" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!config) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-gray-600 dark:text-gray-400 text-center">{t("ui.no_config")}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Save Button */}
      {hasChanges && (
        <div className="flex justify-end">
          <Button onClick={handleSave} className="flex items-center gap-2">
            <Save className="h-4 w-4" />
            {t("ui.save_changes")}
          </Button>
        </div>
      )}

      {/* Source Code Block */}
      {showSourceCode && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5" />
              {t("ui.source_title")}
            </CardTitle>
            <CardDescription>{t("ui.source_description")}</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto text-sm">
              <code>{JSON.stringify(config, null, 2)}</code>
            </pre>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            {t("tab.general")}
          </TabsTrigger>
          <TabsTrigger value="nonebot" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            {t("tab.nonebot")}
          </TabsTrigger>
          <TabsTrigger value="api" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            {t("tab.api")}
          </TabsTrigger>
          <TabsTrigger value="subs" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            {t("tab.subs")}
          </TabsTrigger>
        </TabsList>

        {/* General Tab */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("config.analyze.title")}</CardTitle>
              <CardDescription>{t("config.analyze.desc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigField
                fieldKey="analyze.video"
                label={t("config.analyze.video")}
                description={t("config.analyze.video.desc")}
              >
                <div className="flex items-center justify-between">
                  <div></div>
                  <Switch
                    id="analyze-video"
                    checked={config.analyze.video}
                    onCheckedChange={(checked) => updateConfig(["analyze", "video"], checked)}
                  />
                </div>
              </ConfigField>

              <ConfigField
                fieldKey="analyze.dynamic"
                label={t("config.analyze.dynamic")}
                description={t("config.analyze.dynamic.desc")}
              >
                <div className="flex items-center justify-between">
                  <div></div>
                  <Switch
                    id="analyze-dynamic"
                    checked={config.analyze.dynamic}
                    onCheckedChange={(checked) => updateConfig(["analyze", "dynamic"], checked)}
                  />
                </div>
              </ConfigField>

              <ConfigField
                fieldKey="analyze.column"
                label={t("config.analyze.column")}
                description={t("config.analyze.column.desc")}
              >
                <div className="flex items-center justify-between">
                  <div></div>
                  <Switch
                    id="analyze-column"
                    checked={config.analyze.column}
                    onCheckedChange={(checked) => updateConfig(["analyze", "column"], checked)}
                  />
                </div>
              </ConfigField>

              <ConfigField
                fieldKey="analyze.cd_time"
                label={t("config.analyze.cd_time")}
                description={t("config.analyze.cd_time.desc")}
              >
                <Input
                  id="cd-time"
                  type="number"
                  value={config.analyze.cd_time}
                  onChange={(e) => updateConfig(["analyze", "cd_time"], Number.parseInt(e.target.value))}
                  min="0"
                />
              </ConfigField>
            </CardContent>
          </Card>
        </TabsContent>

        {/* WebUI Tab has been hidden as requested */}

        {/* NoneBot Tab */}
        <TabsContent value="nonebot" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("config.nonebot.title")}</CardTitle>
              <CardDescription>{t("config.nonebot.desc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ConfigField
                  fieldKey="nonebot.block"
                  label={t("config.nonebot.block")}
                  description={t("config.nonebot.block.desc")}
                  disabled
                >
                  <div className="flex items-center justify-between">
                    <div></div>
                    <Switch
                      id="block"
                      checked={config.nonebot.block}
                      onCheckedChange={(checked) => updateConfig(["nonebot", "block"], checked)}
                      disabled
                    />
                  </div>
                </ConfigField>

                <ConfigField
                  fieldKey="nonebot.fallback"
                  label={t("config.nonebot.fallback")}
                  description={t("config.nonebot.fallback.desc")}
                  disabled
                >
                  <div className="flex items-center justify-between">
                    <div></div>
                    <Switch
                      id="fallback"
                      checked={config.nonebot.fallback}
                      onCheckedChange={(checked) => updateConfig(["nonebot", "fallback"], checked)}
                      disabled
                    />
                  </div>
                </ConfigField>

                <ConfigField
                  fieldKey="nonebot.only_to_me"
                  label={t("config.nonebot.only_to_me")}
                  description={t("config.nonebot.only_to_me.desc")}
                  disabled
                >
                  <div className="flex items-center justify-between">
                    <div></div>
                    <Switch
                      id="only-to-me"
                      checked={config.nonebot.only_to_me}
                      onCheckedChange={(checked) => updateConfig(["nonebot", "only_to_me"], checked)}
                      disabled
                    />
                  </div>
                </ConfigField>

                <ConfigField
                  fieldKey="nonebot.command_to_me"
                  label={t("config.nonebot.command_to_me")}
                  description={t("config.nonebot.command_to_me.desc")}
                  disabled
                >
                  <div className="flex items-center justify-between">
                    <div></div>
                    <Switch
                      id="command-to-me"
                      checked={config.nonebot.command_to_me}
                      onCheckedChange={(checked) => updateConfig(["nonebot", "command_to_me"], checked)}
                      disabled
                    />
                  </div>
                </ConfigField>
              </div>

              <ConfigField
                fieldKey="nonebot.cmd_start"
                label={t("config.nonebot.cmd_start")}
                description={t("config.nonebot.cmd_start.desc")}
                disabled
              >
                <Input
                  id="cmd-start"
                  value={config.nonebot.cmd_start}
                  onChange={(e) => updateConfig(["nonebot", "cmd_start"], e.target.value)}
                  disabled
                  className="bg-gray-50 dark:bg-gray-800"
                />
              </ConfigField>

              <div>
                <Label>{t("config.nonebot.cmd_aliases")}</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                  <div>
                    <Label className="text-sm">{t("config.nonebot.cmd_add_sub_label")}</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {config.nonebot.cmd_add_sub.map((cmd: string, index: number) => (
                        <Badge key={index} variant="secondary">
                          {cmd}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <Label className="text-sm">{t("config.nonebot.cmd_remove_sub_label")}</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {config.nonebot.cmd_remove_sub.map((cmd: string, index: number) => (
                        <Badge key={index} variant="secondary">
                          {cmd}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Tab */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("config.api.title")}</CardTitle>
              <CardDescription>{t("config.api.desc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigField
                fieldKey="api.browser_shot_quality"
                label={t("config.api.browser_shot_quality")}
                description={t("config.api.browser_shot_quality.desc")}
              >
                <Input
                  id="browser-quality"
                  type="number"
                  min="10"
                  max="100"
                  value={config.api.browser_shot_quality}
                  onChange={(e) => updateConfig(["api", "browser_shot_quality"], Number.parseInt(e.target.value))}
                />
              </ConfigField>

              <ConfigField
                fieldKey="api.api_health_check_interval"
                label={t("config.api.api_health_check_interval")}
                description={t("config.api.api_health_check_interval.desc")}
              >
                <Input
                  id="health-check"
                  type="number"
                  min="15"
                  value={config.api.api_health_check_interval}
                  onChange={(e) => updateConfig(["api", "api_health_check_interval"], Number.parseInt(e.target.value))}
                />
              </ConfigField>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{t("config.api.request_api.title")}</CardTitle>
                  <CardDescription>{t("config.api.request_api.desc")}</CardDescription>
                </div>
                <Button onClick={addApiEndpoint} size="sm" className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  {t("ui.add_endpoint")}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {config.api.request_api.length === 0 ? (
                <p className="text-gray-500 text-center py-4">{t("ui.no_endpoints")}</p>
              ) : (
                <div className="space-y-4">
                  {config.api.request_api.map((endpoint, index: number) => (
                    <div key={index} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="font-medium">
                          {t("ui.endpoint_number")}
                          {index + 1}
                        </Label>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeApiEndpoint(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <ConfigField
                          fieldKey={`api.request_api[${index}].api`}
                          label={t("config.api.request_api.api")}
                          description={t("config.api.request_api.api.desc")}
                        >
                          <Input
                            id={`api-${index}`}
                            value={endpoint.api}
                            onChange={(e) => updateApiEndpoint(index, "api", e.target.value)}
                            placeholder="https://api.example.com"
                          />
                        </ConfigField>

                        <ConfigField
                          fieldKey={`api.request_api[${index}].token`}
                          label={t("config.api.request_api.token")}
                          description={t("config.api.request_api.token.desc")}
                        >
                          <Input
                            id={`token-${index}`}
                            type="password"
                            value={endpoint.token}
                            onChange={(e) => updateApiEndpoint(index, "token", e.target.value)}
                            placeholder={t("ui.leave_empty_if_not_required")}
                          />
                        </ConfigField>

                        <ConfigField
                          fieldKey={`api.request_api[${index}].weight`}
                          label={t("config.api.request_api.weight")}
                          description={t("config.api.request_api.weight.desc")}
                        >
                          <Input
                            id={`weight-${index}`}
                            type="number"
                            min="1"
                            value={endpoint.weight}
                            onChange={(e) => updateApiEndpoint(index, "weight", Number.parseInt(e.target.value))}
                          />
                        </ConfigField>

                        <ConfigField
                          fieldKey={`api.request_api[${index}].enable`}
                          label={t("config.api.request_api.enable")}
                          description={t("config.api.request_api.enable.desc")}
                        >
                          <div className="flex items-center justify-between">
                            <div></div>
                            <Switch
                              id={`enable-${index}`}
                              checked={endpoint.enable}
                              onCheckedChange={(checked) => updateApiEndpoint(index, "enable", checked)}
                            />
                          </div>
                        </ConfigField>
                      </div>

                      <ConfigField
                        fieldKey={`api.request_api[${index}].note`}
                        label={t("config.api.request_api.note")}
                        description={t("config.api.request_api.note.desc")}
                      >
                        <Textarea
                          id={`note-${index}`}
                          value={endpoint.note}
                          onChange={(e) => updateApiEndpoint(index, "note", e.target.value)}
                          placeholder={t("ui.optional_description_or_note")}
                          rows={2}
                        />
                      </ConfigField>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Subscriptions Tab */}
        <TabsContent value="subs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("config.subs.title")}</CardTitle>
              <CardDescription>{t("config.subs.desc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigField
                fieldKey="subs.dynamic_interval"
                label={t("config.subs.dynamic_interval")}
                description={t("config.subs.dynamic_interval.desc")}
              >
                <Input
                  id="dynamic-interval"
                  type="number"
                  min="15"
                  value={config.subs.dynamic_interval}
                  onChange={(e) => updateConfig(["subs", "dynamic_interval"], Number.parseInt(e.target.value))}
                />
              </ConfigField>

              <ConfigField
                fieldKey="subs.live_interval"
                label={t("config.subs.live_interval")}
                description={t("config.subs.live_interval.desc")}
              >
                <Input
                  id="live-interval"
                  type="number"
                  min="10"
                  value={config.subs.live_interval}
                  onChange={(e) => updateConfig(["subs", "live_interval"], Number.parseInt(e.target.value))}
                />
              </ConfigField>

              <ConfigField
                fieldKey="subs.push_delay"
                label={t("config.subs.push_delay")}
                description={t("config.subs.push_delay.desc")}
              >
                <Input
                  id="push-delay"
                  type="number"
                  min="0"
                  value={config.subs.push_delay}
                  onChange={(e) => updateConfig(["subs", "push_delay"], Number.parseInt(e.target.value))}
                />
              </ConfigField>

              <div>
                <div className="mb-4">
                  <Label>{t("config.subs.users")}</Label>
                </div>
                <div className="space-y-4">
                  {Object.keys(config.subs.users).length === 0 ? (
                    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p className="text-sm">{t("ui.no_users")}</p>
                    </div>
                  ) : (
                    Object.keys(config.subs.users).map((userId) => (
                      <UserConfigEditor
                        key={userId}
                        userId={userId}
                        userConfig={config.subs.users[userId]}
                        onConfigChange={(newConfig) => {
                          const newUsers = { ...config.subs.users }
                          newUsers[userId] = newConfig
                          updateConfig(["subs", "users"], newUsers)
                        }}
                        onDeleteUser={(userIdToDelete) => {
                          const newUsers = { ...config.subs.users }
                          delete newUsers[userIdToDelete]
                          updateConfig(["subs", "users"], newUsers)
                        }}
                      />
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
