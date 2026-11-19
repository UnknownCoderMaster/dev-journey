<script setup lang="ts">
import { ref } from 'vue'
import type { CardListItem, CardStatusValue } from '@/types'
import { STATUS_TONES } from '@/composables/useCardStatus'
import AppBadge from '@/components/ui/AppBadge.vue'
import CardItem from './CardItem.vue'

const props = defineProps<{
  title: string
  status: CardStatusValue
  cards: CardListItem[]
  pending: Set<number>
  /** Sudrab o'tilayotgan karta bormi — bo'sh ustunni belgilash uchun */
  dragging: boolean
}>()

const emit = defineEmits<{
  open: [card: CardListItem]
  drop: [status: CardStatusValue]
  dragstart: [card: CardListItem]
  dragend: []
}>()

const over = ref(false)

function onDragOver(event: DragEvent): void {
  // preventDefault bo'lmasa brauzer drop'ga ruxsat bermaydi
  event.preventDefault()
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
  over.value = true
}

function onDragLeave(event: DragEvent): void {
  // Ichki elementga o'tganda leave ishlamasligi kerak
  const related = event.relatedTarget as Node | null
  if (related && (event.currentTarget as HTMLElement).contains(related)) return

  over.value = false
}

function onDrop(event: DragEvent): void {
  event.preventDefault()
  over.value = false
  emit('drop', props.status)
}
</script>

<template>
  <section
    class="column"
    :class="{ 'column--over': over, 'column--target': dragging && !over }"
    :aria-label="title"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <header class="column__head">
      <div class="u-row">
        <AppBadge :tone="STATUS_TONES[status]" dot>{{ title }}</AppBadge>
      </div>
      <span class="column__count">{{ cards.length }}</span>
    </header>

    <div class="column__body">
      <CardItem
        v-for="card in cards"
        :key="card.id"
        :card="card"
        :busy="pending.has(card.id)"
        @open="emit('open', $event)"
        @dragstart="emit('dragstart', $event)"
        @dragend="emit('dragend')"
      />

      <p v-if="cards.length === 0" class="column__empty">
        {{ dragging ? 'Shu yerga tashlang' : "Karta yo'q" }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.column {
  display: flex;
  flex-direction: column;
  min-height: 180px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  transition:
    border-color var(--transition),
    background-color var(--transition);
}

.column--target {
  border-style: dashed;
}

.column--over {
  border-color: var(--c-accent-500);
  border-style: solid;
  background: var(--c-accent-50);
}

.column__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-2);
  padding: var(--sp-3) var(--sp-3) var(--sp-2);
}

.column__count {
  color: var(--text-muted);
  font-size: var(--fs-xs);
  font-variant-numeric: tabular-nums;
}

.column__body {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  padding: 0 var(--sp-3) var(--sp-3);
}

.column__empty {
  padding: var(--sp-5) var(--sp-2);
  color: var(--text-muted);
  font-size: var(--fs-sm);
  text-align: center;
}
</style>
