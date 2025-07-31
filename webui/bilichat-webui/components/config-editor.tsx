"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Save, Settings, Globe, Bot, Database, Bell, Plus, Trash2, Code, AlertCircle, Loader2 } from "lucide-react"
import { useI18n } from "@/lib/i18n"
import { ConfigField } from "./config-field"
import { useConfig } from "@/hooks/use-config"

interface ConfigEditorProps {
  showSourceCode: boolean
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

  const updateApiEndpoint = (index: number, field: string, value: any) => {
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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            {t("tab.general")}
          </TabsTrigger>
          <TabsTrigger value="webui" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            {t("tab.webui")}
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

        {/* WebUI Tab */}
        <TabsContent value="webui" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("config.webui.title")}</CardTitle>
              <CardDescription>{t("config.webui.desc")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigField
                fieldKey="webui.enable"
                label={t("config.webui.enable")}
                description={t("config.webui.enable.desc")}
                disabled
              >
                <div className="flex items-center justify-between">
                  <div></div>
                  <Switch
                    id="webui-enable"
                    checked={config.webui.enable}
                    onCheckedChange={(checked) => updateConfig(["webui", "enable"], checked)}
                    disabled
                  />
                </div>
              </ConfigField>

              <ConfigField
                fieldKey="webui.api_path"
                label={t("config.webui.api_path")}
                description={t("config.webui.api_path.desc")}
                disabled
              >
                <Input
                  id="webui-path"
                  value={config.webui.api_path}
                  onChange={(e) => updateConfig(["webui", "api_path"], e.target.value)}
                  disabled
                  className="bg-gray-50 dark:bg-gray-800"
                />
              </ConfigField>

              <ConfigField
                fieldKey="webui.jwt_secret_key"
                label={t("config.webui.jwt_secret_key")}
                description={t("config.webui.jwt_secret_key.desc")}
                disabled
              >
                <Input
                  id="webui-jwt-key"
                  type="password"
                  value={config.webui.jwt_secret_key}
                  onChange={(e) => updateConfig(["webui", "jwt_secret_key"], e.target.value)}
                  disabled
                  className="bg-gray-50 dark:bg-gray-800"
                />
              </ConfigField>
            </CardContent>
          </Card>
        </TabsContent>

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
                  {config.api.request_api.map((endpoint: any, index: number) => (
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
                <Label>{t("config.subs.users")}</Label>
                <div className="mt-2">
                  {Object.keys(config.subs.users).length === 0 ? (
                    <p className="text-sm text-gray-600 dark:text-gray-400">{t("ui.no_users")}</p>
                  ) : (
                    <div className="space-y-2">
                      {Object.keys(config.subs.users).map((userId, index) => (
                        <Badge key={index} variant="secondary">
                          User {userId}
                        </Badge>
                      ))}
                    </div>
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
