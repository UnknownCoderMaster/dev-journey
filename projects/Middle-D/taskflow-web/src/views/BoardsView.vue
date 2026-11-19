<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useBoardsStore } from '@/stores/boards'
import { useToastStore } from '@/stores/toasts'
import { formatDate } from '@/composables/useFormat'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppField from '@/components/ui/AppField.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppState from '@/components/ui/AppState.vue'

const boards = useBoardsStore()
const toasts = useToastStore()

const failed = ref(false)
const createOpen = ref(false)
const submitting = ref(false)

const name = ref('')
const description = ref('')
const createError = ref('')

const controller = new AbortController()

async function load(): Promise<void> {
  failed.value = false
  try {
    await boards.load(controller.signal)
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') return
    failed.value = true
    toasts.error(error)
  }
}

function openCreate(): void {
  name.value = ''
  description.value = ''
  createError.value = ''
  createOpen.value = true
}

async function submitCreate(): Promise<void> {
  createError.value = ''

  if (!name.value.trim()) {
    createError.value = 'Doska nomini kiriting'
    return
  }

  submitting.value = true
  try {
    await boards.create({
      name: name.value.trim(),
      description: description.value.trim() || null,
    })

    createOpen.value = false
    toasts.success('Doska yaratildi')
  } catch (error) {
    createError.value = error instanceof Error ? error.message : 'Yaratishda xato'
  } finally {
    submitting.value = false
  }
}

onMounted(load)
onUnmounted(() => controller.abort())
</script>

<template>
  <div class="page">
    <header class="page__head">
      <div>
        <h1 class="page__title">Doskalar</h1>
        <p class="page__meta">
          <template v-if="boards.loaded">
            {{ boards.items.length }} doska · {{ boards.totalCards }} karta
          </template>
          <template v-else>Yuklanmoqda…</template>
        </p>
      </div>

      <div class="page__actions">
        <div class="page__search">
          <AppField
            v-model="boards.query"
            label="Qidirish"
            type="search"
            placeholder="Nom, izoh yoki egasi"
          />
        </div>

        <AppButton variant="primary" @click="openCreate">Yangi doska</AppButton>
      </div>
    </header>

    <AppState v-if="boards.loading && !boards.loaded" kind="loading" :rows="4" />

    <AppState
      v-else-if="failed"
      kind="error"
      title="Ma'lumot yuklanmadi"
      text="Backend ishlab turganini va dev server proxy'si to'g'ri manzilga ko'rsatganini tekshiring."
    >
      <AppButton variant="secondary" @click="load">Qayta urinish</AppButton>
    </AppState>

    <AppState
      v-else-if="boards.items.length === 0"
      kind="empty"
      title="Doska yo'q"
      text="Birinchi doskani yaratib, unga kartalar qo'shishni boshlang."
    >
      <AppButton variant="primary" @click="openCreate">Yangi doska</AppButton>
    </AppState>

    <AppState
      v-else-if="boards.filtered.length === 0"
      kind="empty"
      title="Natija topilmadi"
      :text="`Qidiruv so'zi: ${boards.query} — mos doska topilmadi.`"
    >
      <AppButton variant="ghost" @click="boards.query = ''">Filtrni tozalash</AppButton>
    </AppState>

    <ul v-else class="grid">
      <li v-for="board in boards.filtered" :key="board.id">
        <RouterLink :to="{ name: 'board', params: { id: board.id } }" class="card">
          <div class="card__head">
            <h2 class="card__title u-truncate">{{ board.name }}</h2>
            <AppBadge tone="neutral">{{ board.cardsCount }}</AppBadge>
          </div>

          <p v-if="board.description" class="card__text">{{ board.description }}</p>
          <p v-else class="card__text card__text--empty">Izoh yo'q</p>

          <dl class="card__foot">
            <div>
              <dt>Egasi</dt>
              <dd class="u-truncate">{{ board.owner ?? '—' }}</dd>
            </div>
            <div>
              <dt>Yaratilgan</dt>
              <dd>{{ formatDate(board.createdAt) }}</dd>
            </div>
          </dl>
        </RouterLink>
      </li>
    </ul>

    <AppModal
      :open="createOpen"
      title="Yangi doska"
      description="Doska nomi ro'yxatda ko'rinadi, izoh ixtiyoriy."
      @close="createOpen = false"
    >
      <form class="u-stack" novalidate @submit.prevent="submitCreate">
        <AppField
          v-model="name"
          label="Nom"
          placeholder="Masalan: 2026 yil rejalari"
          required
        />

        <AppField
          v-model="description"
          label="Izoh"
          placeholder="Doska nima uchun kerakligi"
          multiline
          :rows="3"
        />

        <p v-if="createError" class="form-error" role="alert">{{ createError }}</p>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="createOpen = false">Bekor qilish</AppButton>
        <AppButton variant="primary" :loading="submitting" @click="submitCreate">
          Yaratish
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.page {
  max-width: var(--w-container);
  margin: 0 auto;
  padding: var(--sp-6) var(--sp-5) var(--sp-12);
}

.page__head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-5);
  flex-wrap: wrap;
  margin-bottom: var(--sp-6);
  padding-bottom: var(--sp-5);
  border-bottom: 1px solid var(--border-default);
}

.page__title {
  font-size: var(--fs-2xl);
}

.page__meta {
  margin-top: var(--sp-1);
  color: var(--text-muted);
  font-size: var(--fs-sm);
}

.page__actions {
  display: flex;
  align-items: flex-end;
  gap: var(--sp-3);
}

.page__search {
  width: 248px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(268px, 1fr));
  gap: var(--sp-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

.card {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--sp-4);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  color: inherit;
  text-decoration: none;
  transition:
    border-color var(--transition),
    box-shadow var(--transition);
}

.card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--sh-sm);
  text-decoration: none;
}

.card:focus-visible {
  border-color: var(--border-focus);
  box-shadow: var(--ring-focus);
}

.card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-3);
}

.card__title {
  font-size: var(--fs-md);
  font-weight: var(--fw-medium);
}

.card__text {
  margin-top: var(--sp-2);
  flex: 1;
  color: var(--text-secondary);
  font-size: var(--fs-sm);
  line-height: var(--lh-relaxed);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card__text--empty {
  color: var(--text-muted);
  font-style: italic;
}

.card__foot {
  display: flex;
  gap: var(--sp-5);
  margin: var(--sp-4) 0 0;
  padding-top: var(--sp-3);
  border-top: 1px solid var(--border-default);
}

.card__foot dt {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.card__foot dd {
  margin: 1px 0 0;
  font-size: var(--fs-sm);
}

.form-error {
  padding: var(--sp-2) var(--sp-3);
  background: var(--c-danger-50);
  border-left: 3px solid var(--c-danger-500);
  border-radius: var(--r-sm);
  color: var(--c-danger-500);
  font-size: var(--fs-sm);
}

@media (max-width: 720px) {
  .page__head {
    align-items: stretch;
  }

  .page__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .page__search {
    width: 100%;
  }
}
</style>
