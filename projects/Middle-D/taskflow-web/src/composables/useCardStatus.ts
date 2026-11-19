import { CardStatus, type CardStatusName, type CardStatusValue } from '@/types'

/**
 * Backend status qiymatini ikki xil shaklda beradi:
 *   - REST javoblarida raqam (0 / 1 / 2), chunki JsonStringEnumConverter
 *     sozlanmagan;
 *   - SignalR hodisalarida satr ("Todo" / "InProgress" / "Done"), chunki
 *     hub'da `request.Status.ToString()` chaqirilgan.
 *
 * Shuning uchun ikkisini ham bitta ichki shaklga keltiramiz.
 */

const BY_NAME: Record<string, CardStatusValue> = {
  todo: CardStatus.Todo,
  inprogress: CardStatus.InProgress,
  'in-progress': CardStatus.InProgress,
  in_progress: CardStatus.InProgress,
  done: CardStatus.Done,
}

export function normalizeStatus(value: unknown): CardStatusValue {
  if (typeof value === 'number') {
    if (value === CardStatus.InProgress) return CardStatus.InProgress
    if (value === CardStatus.Done) return CardStatus.Done
    return CardStatus.Todo
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()

    // Satr ichida raqam kelishi ham mumkin: "1"
    if (/^\d+$/.test(trimmed)) {
      return normalizeStatus(Number(trimmed))
    }

    return BY_NAME[trimmed.toLowerCase()] ?? CardStatus.Todo
  }

  return CardStatus.Todo
}

export const STATUS_NAMES: Record<CardStatusValue, CardStatusName> = {
  [CardStatus.Todo]: 'Todo',
  [CardStatus.InProgress]: 'InProgress',
  [CardStatus.Done]: 'Done',
}

export const STATUS_LABELS: Record<CardStatusValue, string> = {
  [CardStatus.Todo]: 'Bajarilishi kerak',
  [CardStatus.InProgress]: 'Jarayonda',
  [CardStatus.Done]: 'Tugallangan',
}

export const STATUS_TONES: Record<CardStatusValue, 'neutral' | 'warning' | 'success'> = {
  [CardStatus.Todo]: 'neutral',
  [CardStatus.InProgress]: 'warning',
  [CardStatus.Done]: 'success',
}

export function statusLabel(value: unknown): string {
  return STATUS_LABELS[normalizeStatus(value)]
}
