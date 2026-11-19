<script setup lang="ts">
import { computed } from 'vue'
import type { CardListItem } from '@/types'
import { describeDeadline } from '@/composables/useFormat'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const props = defineProps<{
  card: CardListItem
  /** Status o'zgarishi serverga ketayotgan bo'lsa */
  busy?: boolean
}>()

const emit = defineEmits<{
  open: [card: CardListItem]
  dragstart: [card: CardListItem]
  dragend: []
}>()

const deadline = computed(() => describeDeadline(props.card.deadline))

function onDragStart(event: DragEvent): void {
  if (!event.dataTransfer) return

  event.dataTransfer.effectAllowed = 'move'
  // Ba'zi brauzerlar bo'sh dataTransfer bilan drag'ni boshlamaydi
  event.dataTransfer.setData('text/plain', String(props.card.id))

  emit('dragstart', props.card)
}
</script>

<template>
  <article
    class="item"
    :class="{ 'item--busy': busy }"
    :draggable="!busy"
    tabindex="0"
    role="button"
    :aria-label="`Karta: ${card.title}`"
    @click="emit('open', card)"
    @keydown.enter.prevent="emit('open', card)"
    @keydown.space.prevent="emit('open', card)"
    @dragstart="onDragStart"
    @dragend="emit('dragend')"
  >
    <h4 class="item__title">{{ card.title }}</h4>

    <p v-if="card.description" class="item__text">{{ card.description }}</p>

    <div v-if="deadline" class="item__deadline">
      <AppBadge :tone="deadline.tone" dot>{{ deadline.text }}</AppBadge>
    </div>

    <footer class="item__foot">
      <div class="item__counters">
        <span v-if="card.commentsCount > 0" class="item__counter" :title="`${card.commentsCount} izoh`">
          <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
            <path
              d="M2.5 3.5h11v7h-6l-3 2.5v-2.5h-2z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linejoin="round"
            />
          </svg>
          {{ card.commentsCount }}
        </span>

        <span
          v-if="card.attachmentsCount > 0"
          class="item__counter"
          :title="`${card.attachmentsCount} fayl`"
        >
          <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
            <path
              d="M9.5 4.5l-4 4a2 2 0 102.8 2.8l4.2-4.2a3.2 3.2 0 10-4.5-4.5L3.2 7"
              fill="none"
              stroke="currentColor"
              stroke-width="1.2"
              stroke-linecap="round"
            />
          </svg>
          {{ card.attachmentsCount }}
        </span>
      </div>

      <AppAvatar v-if="card.assignee" :name="card.assignee" />
      <span v-else class="item__unassigned" title="Mas'ul belgilanmagan">—</span>
    </footer>
  </article>
</template>

<style scoped>
.item {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  padding: var(--sp-3);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--r-md);
  cursor: pointer;
  transition:
    border-color var(--transition),
    box-shadow var(--transition),
    opacity var(--transition);
}

.item:hover {
  border-color: var(--border-strong);
  box-shadow: var(--sh-xs);
}

.item:focus-visible {
  border-color: var(--border-focus);
  box-shadow: var(--ring-focus);
}

.item:active {
  cursor: grabbing;
}

.item--busy {
  opacity: 0.6;
  cursor: progress;
}

.item__title {
  font-size: var(--fs-base);
  font-weight: var(--fw-medium);
  line-height: var(--lh-normal);
}

.item__text {
  color: var(--text-secondary);
  font-size: var(--fs-sm);
  line-height: var(--lh-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item__deadline {
  display: flex;
}

.item__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-2);
  margin-top: var(--sp-1);
}

.item__counters {
  display: flex;
  gap: var(--sp-3);
}

.item__counter {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-1);
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.item__unassigned {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}
</style>
