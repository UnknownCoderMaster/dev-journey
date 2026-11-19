import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { cardsApi } from '@/api/resources'
import { CardStatus, type CardListItem, type CardStatusValue } from '@/types'
import { normalizeStatus } from '@/composables/useCardStatus'

export interface Column {
  status: CardStatusValue
  title: string
  cards: CardListItem[]
}

export const useCardsStore = defineStore('cards', () => {
  const boardId = ref<number | null>(null)
  const items = ref<CardListItem[]>([])
  const loading = ref(false)
  /** Status o'zgarishi ketayotgan kartalar — UI ularni band ko'rsatadi */
  const pending = ref<Set<number>>(new Set())

  const columns = computed<Column[]>(() => [
    {
      status: CardStatus.Todo,
      title: 'Bajarilishi kerak',
      cards: items.value.filter((c) => c.status === CardStatus.Todo),
    },
    {
      status: CardStatus.InProgress,
      title: 'Jarayonda',
      cards: items.value.filter((c) => c.status === CardStatus.InProgress),
    },
    {
      status: CardStatus.Done,
      title: 'Tugallangan',
      cards: items.value.filter((c) => c.status === CardStatus.Done),
    },
  ])

  function byId(id: number): CardListItem | undefined {
    return items.value.find((c) => c.id === id)
  }

  function reset(): void {
    boardId.value = null
    items.value = []
    pending.value = new Set()
  }

  async function load(id: number, signal?: AbortSignal): Promise<void> {
    boardId.value = id
    loading.value = true
    try {
      const list = await cardsApi.list(id, signal)
      // Status REST da raqam keladi, lekin ishonmay normallashtirib qo'yamiz
      items.value = list.map((c) => ({ ...c, status: normalizeStatus(c.status) }))
    } finally {
      loading.value = false
    }
  }

  async function create(payload: {
    title: string
    description?: string | null
    deadline?: string | null
  }): Promise<void> {
    if (boardId.value === null) return

    await cardsApi.create(boardId.value, {
      title: payload.title,
      description: payload.description ?? null,
      deadline: payload.deadline ?? null,
      // Backend'da foydalanuvchilar ro'yxati endpoint'i yo'q,
      // shuning uchun mas'ulni UI dan tanlab bo'lmaydi.
      assigneeId: null,
    })

    // POST javobi EF entity'si — GET projeksiyasiga mos kelmaydi.
    // Ro'yxatni qayta o'qiymiz, SignalR hodisasi ham kelishi mumkin.
    await load(boardId.value)
  }

  /**
   * Statusni o'zgartiradi. Optimistik: UI darhol yangilanadi,
   * server xato bersa orqaga qaytariladi.
   */
  async function moveTo(cardId: number, status: CardStatusValue): Promise<void> {
    if (boardId.value === null) return

    const card = byId(cardId)
    if (!card || card.status === status) return

    const previous = card.status
    card.status = status

    const busy = new Set(pending.value)
    busy.add(cardId)
    pending.value = busy

    try {
      await cardsApi.updateStatus(boardId.value, cardId, status)
    } catch (error) {
      card.status = previous
      throw error
    } finally {
      const next = new Set(pending.value)
      next.delete(cardId)
      pending.value = next
    }
  }

  async function remove(cardId: number): Promise<void> {
    if (boardId.value === null) return

    await cardsApi.remove(boardId.value, cardId)
    items.value = items.value.filter((c) => c.id !== cardId)
  }

  /* ─── SignalR hodisalari ──────────────────────────────── */

  function applyStatusFromEvent(cardId: number, status: CardStatusValue): void {
    const card = byId(cardId)
    if (card) card.status = status
  }

  function applyDeleteFromEvent(cardId: number): void {
    items.value = items.value.filter((c) => c.id !== cardId)
  }

  function bumpCommentsCount(cardId: number, delta: number): void {
    const card = byId(cardId)
    if (card) {
      card.commentsCount = Math.max(0, (card.commentsCount ?? 0) + delta)
    }
  }

  function bumpAttachmentsCount(cardId: number, delta: number): void {
    const card = byId(cardId)
    if (card) {
      card.attachmentsCount = Math.max(0, (card.attachmentsCount ?? 0) + delta)
    }
  }

  return {
    boardId,
    items,
    loading,
    pending,
    columns,
    byId,
    reset,
    load,
    create,
    moveTo,
    remove,
    applyStatusFromEvent,
    applyDeleteFromEvent,
    bumpCommentsCount,
    bumpAttachmentsCount,
  }
})
