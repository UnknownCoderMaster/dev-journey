<script setup lang="ts">
import AppButton from '@/components/ui/AppButton.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="nf">
    <p class="nf__code">404</p>
    <h1 class="nf__title">Sahifa topilmadi</h1>
    <p class="nf__text">
      So'ralgan manzil mavjud emas yoki o'chirilgan bo'lishi mumkin.
    </p>

    <div class="nf__actions">
      <AppButton variant="primary" @click="router.push({ name: 'boards' })">
        Doskalarga qaytish
      </AppButton>
    </div>
  </div>
</template>

<style scoped>
.nf {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: var(--sp-8) var(--sp-4);
  text-align: center;
}

.nf__code {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: var(--fs-sm);
  letter-spacing: 0.08em;
}

.nf__title {
  margin-top: var(--sp-3);
  font-size: var(--fs-2xl);
}

.nf__text {
  margin-top: var(--sp-2);
  max-width: 44ch;
  color: var(--text-muted);
  font-size: var(--fs-base);
  line-height: var(--lh-relaxed);
}

.nf__actions {
  margin-top: var(--sp-6);
}
</style>
