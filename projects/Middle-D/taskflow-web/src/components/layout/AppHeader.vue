<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppButton from '@/components/ui/AppButton.vue'

const auth = useAuthStore()
const router = useRouter()

const menuOpen = ref(false)

const roleLabel = computed(() =>
  auth.user?.role === 'Admin' ? 'Administrator' : 'Xodim',
)

function logout(): void {
  menuOpen.value = false
  auth.logout()
  void router.push({ name: 'login' })
}
</script>

<template>
  <header class="header">
    <RouterLink :to="{ name: 'boards' }" class="header__brand">
      <span class="header__mark" aria-hidden="true">TF</span>
      <span class="header__name">TaskFlow</span>
    </RouterLink>

    <nav class="header__nav" aria-label="Asosiy menyu">
      <RouterLink :to="{ name: 'boards' }" class="header__link">Doskalar</RouterLink>
    </nav>

    <div class="header__spacer" />

    <div v-if="auth.user" class="header__user">
      <button
        type="button"
        class="header__trigger"
        :aria-expanded="menuOpen"
        aria-haspopup="true"
        @click="menuOpen = !menuOpen"
      >
        <AppAvatar :name="auth.user.fullName" />
        <span class="header__user-name u-truncate">{{ auth.user.fullName }}</span>
        <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
          <path
            d="M4 6.5l4 4 4-4"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          />
        </svg>
      </button>

      <!-- Fon bosilganda yopish -->
      <div v-if="menuOpen" class="header__overlay" @click="menuOpen = false" />

      <div v-if="menuOpen" class="header__menu" role="menu">
        <div class="header__menu-head">
          <p class="header__menu-name">{{ auth.user.fullName }}</p>
          <p class="header__menu-email u-truncate">{{ auth.user.email }}</p>
          <p class="header__menu-role">{{ roleLabel }}</p>
        </div>

        <div class="header__menu-foot">
          <AppButton variant="secondary" size="sm" block @click="logout">
            Chiqish
          </AppButton>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  gap: var(--sp-5);
  height: var(--h-header);
  padding: 0 var(--sp-5);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-default);
}

.header__brand {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  color: var(--text-primary);
  text-decoration: none;
}

.header__brand:hover {
  text-decoration: none;
}

.header__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--c-accent-500);
  border-radius: var(--r-sm);
  color: var(--text-inverse);
  font-size: 0.625rem;
  font-weight: var(--fw-semibold);
  letter-spacing: 0.04em;
}

.header__name {
  font-size: var(--fs-md);
  font-weight: var(--fw-semibold);
  letter-spacing: -0.01em;
}

.header__nav {
  display: flex;
  gap: var(--sp-1);
}

.header__link {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 var(--sp-3);
  border-radius: var(--r-sm);
  color: var(--text-secondary);
  font-size: var(--fs-base);
  text-decoration: none;
}

.header__link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  text-decoration: none;
}

.header__link.router-link-active {
  background: var(--bg-active);
  color: var(--text-primary);
  font-weight: var(--fw-medium);
}

.header__spacer {
  flex: 1;
}

.header__user {
  position: relative;
}

.header__trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  max-width: 220px;
  height: 32px;
  padding: 0 var(--sp-2);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--r-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition:
    background-color var(--transition),
    border-color var(--transition);
}

.header__trigger:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
}

.header__user-name {
  font-size: var(--fs-base);
  color: var(--text-primary);
}

.header__overlay {
  position: fixed;
  inset: 0;
  z-index: 1;
}

.header__menu {
  position: absolute;
  top: calc(100% + var(--sp-2));
  right: 0;
  z-index: 2;
  width: 232px;
  background: var(--bg-surface-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--r-md);
  box-shadow: var(--sh-md);
  overflow: hidden;
}

.header__menu-head {
  padding: var(--sp-3) var(--sp-4);
  border-bottom: 1px solid var(--border-default);
}

.header__menu-name {
  font-size: var(--fs-base);
  font-weight: var(--fw-medium);
}

.header__menu-email {
  margin-top: 1px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.header__menu-role {
  margin-top: var(--sp-2);
  color: var(--text-secondary);
  font-size: var(--fs-xs);
}

.header__menu-foot {
  padding: var(--sp-3) var(--sp-4);
}

@media (max-width: 640px) {
  .header {
    gap: var(--sp-3);
    padding: 0 var(--sp-4);
  }

  .header__name,
  .header__user-name {
    display: none;
  }
}
</style>
