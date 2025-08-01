"use client"

import type { ReactNode } from "react"
import { Label } from "@/components/ui/label"
import { useI18n } from "@/lib/i18n"

interface ConfigFieldProps {
  fieldKey: string
  label: string
  description?: string
  children: ReactNode
  disabled?: boolean
}

export function ConfigField({ fieldKey, label, description, children, disabled }: ConfigFieldProps) {
  const { t } = useI18n()

  return (
    <div className="space-y-2">
      <div>
        <Label htmlFor={fieldKey} className={disabled ? "text-gray-500" : ""}>
          {label} <span className="text-xs text-gray-400 dark:text-gray-500 font-mono ml-2">({fieldKey})</span>
        </Label>
        {description && <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{description}</p>}
      </div>
      {children}
      {disabled && <p className="text-sm text-gray-500 mt-1">{t("ui.readonly_field")}</p>}
    </div>
  )
}
