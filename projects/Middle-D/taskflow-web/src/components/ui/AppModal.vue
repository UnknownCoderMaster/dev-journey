<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    width?: string
    /** Fon bosilganda yopilmasin — ma'lumot yo'qolmasligi uchun */
    persistent?: boolean
  }>(),
  { width: '460px', persistent: false },
)

const emit = defineEmits<{ close: [] }>()

const panel = ref<HTMLElement | null>(null)
const titleId = useId()
const descId = useId()

let previouslyFocused: HTMLElement | null = null

function close(): void {
  emit('close')
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    event.stopPropagation()
    close()
    return
  }

  // Fokus modal ichida qolsin
  if (event.key !== 'Tab' || !panel.value) return

  const focusable = panel.value.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
  )
  if (focusable.length === 0) return

  const first = focusable[0]!
  const last = focusable[focusable.length - 1]!

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      previouslyFocused = document.activeElement as HTMLElement | null
      document.body.style.overflow = 'hidden'

      await nextTick()
      const target = panel.value?.querySelector<HTMLElement>(
        'input:not([type="hidden"]), textarea, select, button',
      )
      target?.focus()
    } else {
      document.body.style.overflow = ''
      previouslyFocused?.focus()
      previouslyFocused = null
    }
  },
)

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="modal"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="description ? descId : undefined"
        @keydown="onKeydown"
      >
        <div class="modal__backdrop" @click="persistent ? undefined : close()" />

        <div ref="panel" class="modal__panel" :style="{ maxWidth: width }">
          <header class="modal__header">
            <div>
              <h3 :id="titleId" class="modal__title">{{ title }}</h3>
              <p v-if="description" :id="descId" class="modal__description">
                {{ description }}
              </p>
            </div>

            <button type="button" class="modal__close" aria-label="Yopish" @click="close">
              <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
                <path
                  d="M4 4l8 8M12 4l-8 8"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  fill="none"
                />
              </svg>
            </button>
          </header>

          <div class="modal__body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--sp-8) var(--sp-4);
  overflow-y: auto;
}

.modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(21, 24, 29, 0.42);
  backdrop-filter: blur(1px);
}

.modal__panel {
  position: relative;
  width: 100%;
  margin-top: 4vh;
  background: var(--bg-surface-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-lg);
}

.modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-4);
  padding: var(--sp-5) var(--sp-5) var(--sp-4);
  border-bottom: 1px solid var(--border-default);
}

.modal__title {
  font-size: var(--fs-lg);
}

.modal__description {
  margin-top: var(--sp-1);
  color: var(--text-muted);
  font-size: var(--fs-sm);
}

.modal__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color var(--transition);
}

.modal__close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal__body {
  padding: var(--sp-5);
}

.modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-2);
  padding: var(--sp-4) var(--sp-5);
  border-top: 1px solid var(--border-default);
  background: var(--bg-subtle);
  border-radius: 0 0 var(--r-lg) var(--r-lg);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 120ms ease;
}

.modal-enter-active .modal__panel,
.modal-leave-active .modal__panel {
  transition:
    transform 120ms ease,
    opacity 120ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal__panel,
.modal-leave-to .modal__panel {
  transform: translateY(-6px);
  opacity: 0;
}
</style>
