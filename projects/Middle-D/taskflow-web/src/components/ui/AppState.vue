<script setup lang="ts">
/**
 * Yuklanish / bo'sh / xato holatlari uchun bitta komponent.
 * Uchta holatni bir joyda ushlab turish ularning ko'rinishini
 * butun ilova bo'ylab izchil qiladi.
 */
withDefaults(
  defineProps<{
    kind: 'loading' | 'empty' | 'error'
    title?: string
    text?: string
    /** Skeleton qatorlari soni — loading uchun */
    rows?: number
  }>(),
  { rows: 3 },
)
</script>

<template>
  <!-- Yuklanish: skeleton, chunki spinner sahifa tuzilishini ko'rsatmaydi -->
  <div v-if="kind === 'loading'" class="state state--loading" aria-busy="true">
    <span class="u-sr-only">Yuklanmoqda</span>
    <div v-for="n in rows" :key="n" class="skeleton" :style="{ opacity: 1 - n * 0.12 }" />
  </div>

  <div v-else class="state" :class="`state--${kind}`">
    <div class="state__icon" aria-hidden="true">
      <svg v-if="kind === 'empty'" viewBox="0 0 24 24" width="22" height="22">
        <rect
          x="3.5"
          y="5.5"
          width="17"
          height="13"
          rx="1.5"
          fill="none"
          stroke="currentColor"
          stroke-width="1.4"
        />
        <path d="M3.5 10h17" stroke="currentColor" stroke-width="1.4" />
      </svg>

      <svg v-else viewBox="0 0 24 24" width="22" height="22">
        <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.4" />
        <path d="M12 8v5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
        <circle cx="12" cy="16" r="0.9" fill="currentColor" />
      </svg>
    </div>

    <p v-if="title" class="state__title">{{ title }}</p>
    <p v-if="text" class="state__text">{{ text }}</p>

    <div v-if="$slots.default" class="state__action">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-10) var(--sp-4);
  text-align: center;
}

.state--loading {
  align-items: stretch;
  gap: var(--sp-2);
  padding: var(--sp-2) 0;
}

.state__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-bottom: var(--sp-1);
  border: 1px solid var(--border-default);
  border-radius: var(--r-md);
  color: var(--text-muted);
  background: var(--bg-subtle);
}

.state--error .state__icon {
  border-color: var(--c-danger-500);
  background: var(--c-danger-50);
  color: var(--c-danger-500);
}

.state__title {
  font-size: var(--fs-md);
  font-weight: var(--fw-medium);
  color: var(--text-primary);
}

.state__text {
  max-width: 44ch;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  line-height: var(--lh-relaxed);
}

.state__action {
  margin-top: var(--sp-3);
}

.skeleton {
  height: 56px;
  background: linear-gradient(
    90deg,
    var(--bg-subtle) 25%,
    var(--bg-hover) 50%,
    var(--bg-subtle) 75%
  );
  background-size: 200% 100%;
  border-radius: var(--r-md);
  animation: skeleton 1.3s ease-in-out infinite;
}

@keyframes skeleton {
  from {
    background-position: 200% 0;
  }
  to {
    background-position: -200% 0;
  }
}
</style>
