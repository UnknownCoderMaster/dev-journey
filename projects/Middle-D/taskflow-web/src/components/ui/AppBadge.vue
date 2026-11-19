<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'neutral' | 'accent' | 'success' | 'warning' | 'danger'
    dot?: boolean
  }>(),
  { tone: 'neutral', dot: false },
)
</script>

<template>
  <span :class="['badge', `badge--${tone}`]">
    <span v-if="dot" class="badge__dot" aria-hidden="true" />
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  height: 20px;
  padding: 0 var(--sp-2);
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  font-size: var(--fs-xs);
  font-weight: var(--fw-medium);
  white-space: nowrap;
}

.badge__dot {
  width: 5px;
  height: 5px;
  border-radius: var(--r-full);
  background: currentColor;
}

.badge--neutral {
  background: var(--bg-subtle);
  border-color: var(--border-default);
  color: var(--text-secondary);
}

.badge--accent {
  background: var(--c-accent-50);
  border-color: var(--c-accent-100);
  color: var(--text-accent);
}

.badge--success {
  background: var(--c-success-50);
  color: var(--c-success-500);
}

.badge--warning {
  background: var(--c-warning-50);
  color: var(--c-warning-500);
}

.badge--danger {
  background: var(--c-danger-50);
  color: var(--c-danger-500);
}
</style>
