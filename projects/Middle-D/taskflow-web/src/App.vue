<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppToaster from '@/components/ui/AppToaster.vue'

const route = useRoute()

// Login va register sahifalarida header ko'rsatilmaydi
const showChrome = computed(() => route.meta.public !== true)
</script>

<template>
  <AppHeader v-if="showChrome" />

  <main :class="['shell', { 'shell--bare': !showChrome }]">
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>

  <AppToaster />
</template>

<style scoped>
.shell {
  min-height: calc(100vh - var(--h-header));
}

.shell--bare {
  min-height: 100vh;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 100ms ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
