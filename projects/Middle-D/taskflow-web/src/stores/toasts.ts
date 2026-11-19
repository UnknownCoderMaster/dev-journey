import { ref } from 'vue'
import { defineStore } from 'pinia'
import { ApiError } from '@/api/client'

export type ToastKind = 'info' | 'success' | 'warning' | 'danger'

export interface Toast {
  id: number
  kind: ToastKind
  text: string
  /** 0 bo'lsa o'zi yopilmaydi — foydalanuvchi yopadi */
  timeout: number
}

let nextId = 1

export const useToastStore = defineStore('toasts', () => {
  const items = ref<Toast[]>([])

  function dismiss(id: number): void {
    items.value = items.value.filter((t) => t.id !== id)
  }

  function push(kind: ToastKind, text: string, timeout = 4500): number {
    const id = nextId++
    items.value = [...items.value, { id, kind, text, timeout }]

    if (timeout > 0) {
      window.setTimeout(() => dismiss(id), timeout)
    }

    return id
  }

  const info = (text: string) => push('info', text)
  const success = (text: string) => push('success', text)
  const warning = (text: string) => push('warning', text, 6000)

  /**
   * Xatoni ko'rsatadi. 401 ni jim o'tkazib yuboradi — u holatda
   * foydalanuvchi allaqachon login sahifasiga yo'naltiriladi va
   * ikkita xabar ko'rsatish ortiqcha shovqin bo'ladi.
   */
  function error(cause: unknown, fallback = 'Kutilmagan xato'): void {
    if (cause instanceof DOMException && cause.name === 'AbortError') {
      return
    }

    if (cause instanceof ApiError) {
      if (cause.status === 401) return
      push('danger', cause.message, 7000)
      return
    }

    if (cause instanceof Error) {
      push('danger', cause.message, 7000)
      return
    }

    push('danger', fallback, 7000)
  }

  return { items, push, info, success, warning, error, dismiss }
})
