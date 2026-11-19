<script setup lang="ts">
import { computed } from 'vue'
import { initials } from '@/composables/useFormat'

const props = withDefaults(
  defineProps<{
    name: string | null | undefined
    size?: 'sm' | 'md'
  }>(),
  { size: 'sm' },
)

const label = computed(() => initials(props.name))
</script>

<template>
  <span :class="['avatar', `avatar--${size}`]" :title="name ?? undefined" aria-hidden="true">
    {{ label }}
  </span>
</template>

<style scoped>
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--bg-subtle);
  border: 1px solid var(--border-default);
  border-radius: var(--r-full);
  color: var(--text-secondary);
  font-weight: var(--fw-medium);
  letter-spacing: 0.02em;
  user-select: none;
}

.avatar--sm {
  width: 22px;
  height: 22px;
  font-size: 0.625rem;
}

.avatar--md {
  width: 30px;
  height: 30px;
  font-size: var(--fs-xs);
}
</style>
