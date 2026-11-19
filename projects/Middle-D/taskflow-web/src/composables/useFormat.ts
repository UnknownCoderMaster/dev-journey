/**
 * Sana va o'lcham formatlash.
 *
 * Backend `DateTime.UtcNow` saqlaydi, lekin ustun `timestamp without
 * time zone` bo'lsa JSON da zona belgisisiz keladi ("2026-11-19T08:14:22").
 * Brauzer bunday satrni **mahalliy** vaqt deb o'qiydi va natijada
 * soat farqi paydo bo'ladi. Shuning uchun zona belgisi yo'q bo'lsa
 * UTC deb talqin qilamiz.
 */

function parse(value: string | null | undefined): Date | null {
  if (!value) return null

  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/.test(value)
  const date = new Date(hasZone ? value : `${value}Z`)

  return Number.isNaN(date.getTime()) ? null : date
}

const dateFormatter = new Intl.DateTimeFormat('uz-UZ', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

const dateTimeFormatter = new Intl.DateTimeFormat('uz-UZ', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

const timeFormatter = new Intl.DateTimeFormat('uz-UZ', {
  hour: '2-digit',
  minute: '2-digit',
})

export function formatDate(value: string | null | undefined): string {
  const date = parse(value)
  return date ? dateFormatter.format(date) : '—'
}

export function formatDateTime(value: string | null | undefined): string {
  const date = parse(value)
  return date ? dateTimeFormatter.format(date) : '—'
}

export function formatTime(value: string | null | undefined): string {
  const date = parse(value)
  return date ? timeFormatter.format(date) : '—'
}

/** "3 kun oldin", "2 soat oldin" ko'rinishida. */
export function formatRelative(value: string | null | undefined): string {
  const date = parse(value)
  if (!date) return '—'

  const diffMs = Date.now() - date.getTime()
  const diffMin = Math.round(diffMs / 60_000)

  if (Math.abs(diffMin) < 1) return 'hozir'

  const units: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ['minute', 60],
    ['hour', 24],
    ['day', 7],
    ['week', 4.345],
    ['month', 12],
  ]

  const formatter = new Intl.RelativeTimeFormat('uz', { numeric: 'auto' })

  let value_ = -diffMin
  for (const [unit, limit] of units) {
    if (Math.abs(value_) < limit) {
      return formatter.format(Math.round(value_), unit)
    }
    value_ /= limit
  }

  return formatter.format(Math.round(value_), 'year')
}

export interface DeadlineState {
  text: string
  tone: 'neutral' | 'warning' | 'danger'
  /** Muddat o'tganmi */
  overdue: boolean
}

/** Muddatni holat bilan qaytaradi — UI rangni shunga qarab tanlaydi. */
export function describeDeadline(value: string | null | undefined): DeadlineState | null {
  const date = parse(value)
  if (!date) return null

  const diffMs = date.getTime() - Date.now()
  const diffDays = Math.ceil(diffMs / 86_400_000)

  if (diffMs < 0) {
    return { text: `${formatDate(value)} — muddat o'tdi`, tone: 'danger', overdue: true }
  }

  if (diffDays <= 1) {
    return { text: `${formatDate(value)} — bugun/ertaga`, tone: 'danger', overdue: false }
  }

  if (diffDays <= 3) {
    return { text: `${formatDate(value)} — ${diffDays} kun qoldi`, tone: 'warning', overdue: false }
  }

  return { text: formatDate(value), tone: 'neutral', overdue: false }
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** Ism va familiyadan bosh harflar — avatar uchun. */
export function initials(fullName: string | null | undefined): string {
  if (!fullName) return '?'

  const parts = fullName.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0]!.slice(0, 2).toUpperCase()

  return (parts[0]![0]! + parts[parts.length - 1]![0]!).toUpperCase()
}

/** Konvertatsiya: <input type="datetime-local"> qiymatini ISO ga. */
export function localInputToIso(value: string): string | null {
  if (!value) return null

  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}
