<script setup lang="ts">
import { useToastStore } from '@/stores/toasts'

const toasts = useToastStore()
</script>

<template>
  <Teleport to="body">
    <div class="toaster" role="region" aria-label="Bildirishnomalar">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts.items"
          :key="toast.id"
          :class="['toast', `toast--${toast.kind}`]"
          :role="toast.kind === 'danger' ? 'alert' : 'status'"
        >
          <span class="toast__bar" aria-hidden="true" />
          <p class="toast__text">{{ toast.text }}</p>

          <button
            type="button"
            class="toast__close"
            aria-label="Yopish"
            @click="toasts.dismiss(toast.id)"
          >
            <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
              <path
                d="M4 4l8 8M12 4l-8 8"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                fill="none"
              />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toaster {
  position: fixed;
  right: var(--sp-5);
  bottom: var(--sp-5);
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  width: min(380px, calc(100vw - var(--sp-8)));
  pointer-events: none;
}

.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-3) var(--sp-3) var(--sp-4);
  background: var(--bg-surface-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--r-md);
  box-shadow: var(--sh-md);
  pointer-events: auto;
  overflow: hidden;
}

.toast__bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}

.toast--info .toast__bar {
  background: var(--c-accent-500);
}
.toast--success .toast__bar {
  background: var(--c-success-500);
}
.toast--warning .toast__bar {
  background: var(--c-warning-500);
}
.toast--danger .toast__bar {
  background: var(--c-danger-500);
}

.toast__text {
  flex: 1;
  font-size: var(--fs-sm);
  line-height: var(--lh-normal);
  white-space: pre-line;
}

.toast__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  color: var(--text-muted);
  cursor: pointer;
}

.toast__close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toast-enter-active,
.toast-leave-active {
  transition:
    transform 160ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 160ms ease;
}

.toast-enter-from {
  transform: translateX(16px);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(16px);
  opacity: 0;
}

.toast-leave-active {
  position: absolute;
  right: 0;
  left: 0;
}
</style>
