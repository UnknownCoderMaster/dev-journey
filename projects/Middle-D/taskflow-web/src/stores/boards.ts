import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { boardsApi } from '@/api/resources'
import type { BoardListItem, CreateBoardRequest } from '@/types'

export const useBoardsStore = defineStore('boards', () => {
  const items = ref<BoardListItem[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const query = ref('')

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase()
    if (!q) return items.value

    return items.value.filter(
      (b) =>
        b.name.toLowerCase().includes(q) ||
        (b.description ?? '').toLowerCase().includes(q) ||
        (b.owner ?? '').toLowerCase().includes(q),
    )
  })

  const totalCards = computed(() =>
    items.value.reduce((sum, b) => sum + (b.cardsCount ?? 0), 0),
  )

  function byId(id: number): BoardListItem | undefined {
    return items.value.find((b) => b.id === id)
  }

  async function load(signal?: AbortSignal): Promise<void> {
    loading.value = true
    try {
      items.value = await boardsApi.list(signal)
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function create(payload: CreateBoardRequest): Promise<void> {
    await boardsApi.create(payload)

    // POST javobi EF entity'sini qaytaradi va uning shakli GET /api/boards
    // projeksiyasiga mos kelmaydi. Shuning uchun ro'yxatni serverdan
    // qayta o'qiymiz — backend POST ichida keshni ham tozalagan.
    await load()
  }

  /** SignalR yoki karta o'zgarishidan keyin hisoblagichni mahalliy to'g'rilash. */
  function bumpCardsCount(boardId: number, delta: number): void {
    const board = items.value.find((b) => b.id === boardId)
    if (!board) return

    board.cardsCount = Math.max(0, (board.cardsCount ?? 0) + delta)
  }

  return {
    items,
    loading,
    loaded,
    query,
    filtered,
    totalCards,
    byId,
    load,
    create,
    bumpCardsCount,
  }
})
