<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBoardsStore } from '@/stores/boards'
import { useCardsStore } from '@/stores/cards'
import { useToastStore } from '@/stores/toasts'
import { useBoardHub } from '@/composables/useBoardHub'
import { localInputToIso } from '@/composables/useFormat'
import type { CardListItem, CardStatusValue } from '@/types'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppField from '@/components/ui/AppField.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppState from '@/components/ui/AppState.vue'
import BoardColumn from '@/components/board/BoardColumn.vue'
import CardDrawer from '@/components/board/CardDrawer.vue'

const route = useRoute()
const boards = useBoardsStore()
const cards = useCardsStore()
const toasts = useToastStore()

const boardId = computed(() => Number(route.params.id))
const board = computed(() => boards.byId(boardId.value))

const failed = ref(false)
const selected = ref<CardListItem | null>(null)
const draggedId = ref<number | null>(null)

const drawer = ref<InstanceType<typeof CardDrawer> | null>(null)

/* ─── Yangi karta formasi ─────────────────────────────── */

const createOpen = ref(false)
const submitting = ref(false)
const title = ref('')
const description = ref('')
const deadline = ref('')
const createError = ref('')

/* ─── Realtime ────────────────────────────────────────── */

const hub = useBoardHub({
  // Yangi karta hodisasida faqat ID va sarlavha keladi — ro'yxat
  // projeksiyasiga mos kelmaydi, shuning uchun qayta o'qiymiz.
  onCardCreated: () => {
    void refresh()
  },

  onCommentCreated: (event) => {
    if (selected.value?.id === event.cardId) {
      drawer.value?.applyIncomingComment(event.comment)
    }
  },

  onCommentDeleted: (event) => {
    if (selected.value?.id === event.cardId) {
      drawer.value?.applyRemovedComment(event.commentId)
    }
  },
})

const hubLabel = computed(() => {
  switch (hub.status.value) {
    case 'connected':
      return 'Real vaqt ulangan'
    case 'connecting':
      return 'Ulanmoqda…'
    case 'reconnecting':
      return 'Qayta ulanmoqda…'
    default:
      return 'Real vaqt uzilgan'
  }
})

const hubTone = computed(() => {
  switch (hub.status.value) {
    case 'connected':
      return 'success' as const
    case 'connecting':
    case 'reconnecting':
      return 'warning' as const
    default:
      return 'neutral' as const
  }
})

/* ─── Yuklash ─────────────────────────────────────────── */

let controller = new AbortController()

async function refresh(): Promise<void> {
  try {
    await cards.load(boardId.value)
  } catch (error) {
    toasts.error(error)
  }
}

async function load(): Promise<void> {
  failed.value = false
  controller.abort()
  controller = new AbortController()

  try {
    // Doska sarlavhasi uchun ro'yxat kerak — faqat bir marta o'qiladi
    if (!boards.loaded) {
      await boards.load(controller.signal)
    }

    await cards.load(boardId.value, controller.signal)
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') return
    failed.value = true
    toasts.error(error)
  }
}

watch(boardId, async (id, previous) => {
  if (id === previous) return

  selected.value = null
  await load()
  await hub.connect(id)
})

onMounted(async () => {
  await load()
  await hub.connect(boardId.value)
})

onUnmounted(() => {
  controller.abort()
  cards.reset()
})

/* ─── Drag & drop ─────────────────────────────────────── */

function onDragStart(card: CardListItem): void {
  draggedId.value = card.id
}

function onDragEnd(): void {
  draggedId.value = null
}

async function onDrop(status: CardStatusValue): Promise<void> {
  const cardId = draggedId.value
  draggedId.value = null
  if (cardId === null) return

  try {
    await cards.moveTo(cardId, status)
  } catch (error) {
    toasts.error(error)
  }
}

/* ─── Karta yaratish ──────────────────────────────────── */

function openCreate(): void {
  title.value = ''
  description.value = ''
  deadline.value = ''
  createError.value = ''
  createOpen.value = true
}

async function submitCreate(): Promise<void> {
  createError.value = ''

  if (!title.value.trim()) {
    createError.value = 'Karta sarlavhasini kiriting'
    return
  }

  submitting.value = true
  try {
    await cards.create({
      title: title.value.trim(),
      description: description.value.trim() || null,
      deadline: localInputToIso(deadline.value),
    })

    boards.bumpCardsCount(boardId.value, 1)
    createOpen.value = false
    toasts.success('Karta yaratildi')
  } catch (error) {
    createError.value = error instanceof Error ? error.message : 'Yaratishda xato'
  } finally {
    submitting.value = false
  }
}

function onCardDeleted(): void {
  boards.bumpCardsCount(boardId.value, -1)
}

/** Drawer ochilgan kartaning store'dagi yangi holatini kuzatadi. */
const selectedLive = computed(() =>
  selected.value ? cards.byId(selected.value.id) ?? null : null,
)
</script>

<template>
  <div class="page">
    <nav class="crumbs" aria-label="Navigatsiya">
      <RouterLink :to="{ name: 'boards' }">Doskalar</RouterLink>
      <span aria-hidden="true">/</span>
      <span class="crumbs__current u-truncate">{{ board?.name ?? `#${boardId}` }}</span>
    </nav>

    <header class="page__head">
      <div class="page__head-main">
        <h1 class="page__title">{{ board?.name ?? 'Doska' }}</h1>
        <p v-if="board?.description" class="page__description">{{ board.description }}</p>
        <p class="page__meta">
          <span>{{ cards.items.length }} karta</span>
          <span v-if="board?.owner">· egasi {{ board.owner }}</span>
        </p>
      </div>

      <div class="page__actions">
        <AppBadge :tone="hubTone" dot>{{ hubLabel }}</AppBadge>
        <AppButton variant="secondary" :loading="cards.loading" @click="refresh">
          Yangilash
        </AppButton>
        <AppButton variant="primary" @click="openCreate">Yangi karta</AppButton>
      </div>
    </header>

    <AppState v-if="cards.loading && cards.items.length === 0" kind="loading" :rows="3" />

    <AppState
      v-else-if="failed"
      kind="error"
      title="Doska yuklanmadi"
      text="Backend ishlab turganini tekshiring yoki qayta urinib ko'ring."
    >
      <AppButton variant="secondary" @click="load">Qayta urinish</AppButton>
    </AppState>

    <div v-else class="board">
      <BoardColumn
        v-for="column in cards.columns"
        :key="column.status"
        :title="column.title"
        :status="column.status"
        :cards="column.cards"
        :pending="cards.pending"
        :dragging="draggedId !== null"
        @open="selected = $event"
        @drop="onDrop"
        @dragstart="onDragStart"
        @dragend="onDragEnd"
      />
    </div>

    <p v-if="!failed" class="hint">
      Kartani ustundan ustunga sudrab statusini o'zgartirish mumkin.
    </p>

    <!-- Karta tafsilotlari -->
    <CardDrawer
      ref="drawer"
      :card="selectedLive"
      @close="selected = null"
      @deleted="onCardDeleted"
    />

    <!-- Yangi karta -->
    <AppModal
      :open="createOpen"
      title="Yangi karta"
      description="Karta 'Bajarilishi kerak' ustunida paydo bo'ladi."
      @close="createOpen = false"
    >
      <form class="u-stack" novalidate @submit.prevent="submitCreate">
        <AppField
          v-model="title"
          label="Sarlavha"
          placeholder="Masalan: Hisobot tayyorlash"
          required
        />

        <AppField
          v-model="description"
          label="Tavsif"
          placeholder="Nima qilish kerakligi"
          multiline
          :rows="3"
        />

        <AppField
          v-model="deadline"
          label="Muddat"
          type="datetime-local"
          hint="Ixtiyoriy"
        />

        <p class="form-note">
          Mas'ul tanlash uchun backend'da foydalanuvchilar ro'yxatini qaytaradigan
          endpoint yo'q, shuning uchun karta mas'ulsiz yaratiladi.
        </p>

        <p v-if="createError" class="form-error" role="alert">{{ createError }}</p>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="createOpen = false">Bekor qilish</AppButton>
        <AppButton variant="primary" :loading="submitting" @click="submitCreate">
          Yaratish
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.page {
  max-width: var(--w-container);
  margin: 0 auto;
  padding: var(--sp-5) var(--sp-5) var(--sp-12);
}

.crumbs {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  margin-bottom: var(--sp-3);
  color: var(--text-muted);
  font-size: var(--fs-sm);
}

.crumbs__current {
  color: var(--text-secondary);
  max-width: 320px;
}

.page__head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-5);
  flex-wrap: wrap;
  margin-bottom: var(--sp-5);
  padding-bottom: var(--sp-4);
  border-bottom: 1px solid var(--border-default);
}

.page__head-main {
  min-width: 0;
}

.page__title {
  font-size: var(--fs-2xl);
}

.page__description {
  margin-top: var(--sp-2);
  max-width: 68ch;
  color: var(--text-secondary);
  font-size: var(--fs-base);
  line-height: var(--lh-relaxed);
}

.page__meta {
  display: flex;
  gap: var(--sp-2);
  margin-top: var(--sp-2);
  color: var(--text-muted);
  font-size: var(--fs-sm);
}

.page__actions {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.board {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--sp-4);
  align-items: start;
}

.hint {
  margin-top: var(--sp-4);
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.form-note {
  padding: var(--sp-2) var(--sp-3);
  background: var(--bg-subtle);
  border-left: 3px solid var(--border-strong);
  border-radius: var(--r-sm);
  color: var(--text-secondary);
  font-size: var(--fs-xs);
  line-height: var(--lh-relaxed);
}

.form-error {
  padding: var(--sp-2) var(--sp-3);
  background: var(--c-danger-50);
  border-left: 3px solid var(--c-danger-500);
  border-radius: var(--r-sm);
  color: var(--c-danger-500);
  font-size: var(--fs-sm);
}

@media (max-width: 960px) {
  .board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .page__head {
    align-items: stretch;
  }

  .page__actions {
    flex-wrap: wrap;
  }
}
</style>
