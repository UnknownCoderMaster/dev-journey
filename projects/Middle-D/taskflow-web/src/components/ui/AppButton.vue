<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    loading?: boolean
    block?: boolean
  }>(),
  {
    variant: 'secondary',
    size: 'md',
    type: 'button',
    disabled: false,
    loading: false,
    block: false,
  },
)

const isDisabled = computed(() => props.disabled || props.loading)
</script>

<template>
  <button
    :type="type"
    :disabled="isDisabled"
    :aria-busy="loading || undefined"
    :class="['btn', `btn--${variant}`, `btn--${size}`, { 'btn--block': block }]"
  >
    <span v-if="loading" class="btn__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-2);
  border: 1px solid transparent;
  border-radius: var(--r-md);
  font-weight: var(--fw-medium);
  white-space: nowrap;
  cursor: pointer;
  transition:
    background-color var(--transition),
    border-color var(--transition),
    color var(--transition),
    box-shadow var(--transition);
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.btn--sm {
  height: 28px;
  padding: 0 var(--sp-3);
  font-size: var(--fs-sm);
}

.btn--md {
  height: 34px;
  padding: 0 var(--sp-4);
  font-size: var(--fs-base);
}

.btn--block {
  width: 100%;
}

/* ─── Primary ─────────────────────────────── */
.btn--primary {
  background: var(--c-accent-500);
  border-color: var(--c-accent-500);
  color: var(--text-inverse);
}

.btn--primary:hover:not(:disabled) {
  background: var(--c-accent-600);
  border-color: var(--c-accent-600);
}

.btn--primary:active:not(:disabled) {
  background: var(--c-accent-700);
}

.btn--primary:focus-visible {
  box-shadow: var(--ring-focus);
}

/* ─── Secondary ───────────────────────────── */
.btn--secondary {
  background: var(--bg-surface);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--c-gray-400);
}

.btn--secondary:focus-visible {
  box-shadow: var(--ring-focus);
}

/* ─── Ghost ───────────────────────────────── */
.btn--ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn--ghost:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ─── Danger ──────────────────────────────── */
.btn--danger {
  background: transparent;
  border-color: var(--border-strong);
  color: var(--c-danger-500);
}

.btn--danger:hover:not(:disabled) {
  background: var(--c-danger-50);
  border-color: var(--c-danger-500);
}

/* ─── Spinner ─────────────────────────────── */
.btn__spinner {
  width: 13px;
  height: 13px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: var(--r-full);
  opacity: 0.7;
  animation: btn-spin 600ms linear infinite;
}

@keyframes btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
