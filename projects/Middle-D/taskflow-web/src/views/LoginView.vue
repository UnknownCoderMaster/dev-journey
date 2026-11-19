<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/ui/AppButton.vue'
import AppField from '@/components/ui/AppField.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const formError = ref('')

async function submit(): Promise<void> {
  formError.value = ''

  if (!email.value.trim() || !password.value) {
    formError.value = "Email va parolni kiriting"
    return
  }

  try {
    await auth.login({ email: email.value.trim(), password: password.value })

    const redirect = route.query.redirect
    await router.push(typeof redirect === 'string' ? redirect : { name: 'boards' })
  } catch (error) {
    if (error instanceof ApiError) {
      formError.value = error.message
    } else if (error instanceof Error) {
      formError.value = error.message
    } else {
      formError.value = 'Kirishda kutilmagan xato'
    }
  }
}
</script>

<template>
  <div class="auth">
    <section class="auth__panel">
      <header class="auth__head">
        <span class="auth__mark" aria-hidden="true">TF</span>
        <h1 class="auth__title">TaskFlow</h1>
        <p class="auth__subtitle">Tizimga kirish uchun ma'lumotlaringizni kiriting</p>
      </header>

      <form class="auth__form" novalidate @submit.prevent="submit">
        <AppField
          v-model="email"
          label="Email"
          type="email"
          placeholder="ism@example.com"
          autocomplete="username"
          required
        />

        <AppField
          v-model="password"
          label="Parol"
          type="password"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />

        <p v-if="formError" class="auth__error" role="alert">{{ formError }}</p>

        <AppButton type="submit" variant="primary" block :loading="auth.loading">
          Kirish
        </AppButton>
      </form>

      <footer class="auth__foot">
        <span class="u-muted">Hisobingiz yo'qmi?</span>
        <RouterLink :to="{ name: 'register' }">Ro'yxatdan o'tish</RouterLink>
      </footer>
    </section>

    <p class="auth__note">
      Backend: <code>TaskFlow.API</code> — dev server proxy'si orqali
    </p>
  </div>
</template>

<style scoped>
.auth {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--sp-5);
  min-height: 100vh;
  padding: var(--sp-6) var(--sp-4);
  background: var(--bg-page);
}

.auth__panel {
  width: 100%;
  max-width: 372px;
  padding: var(--sp-8);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-sm);
}

.auth__head {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--sp-6);
  text-align: center;
}

.auth__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  margin-bottom: var(--sp-4);
  background: var(--c-accent-500);
  border-radius: var(--r-md);
  color: var(--text-inverse);
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  letter-spacing: 0.04em;
}

.auth__title {
  font-size: var(--fs-xl);
}

.auth__subtitle {
  margin-top: var(--sp-2);
  color: var(--text-muted);
  font-size: var(--fs-sm);
  line-height: var(--lh-relaxed);
}

.auth__form {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.auth__error {
  padding: var(--sp-2) var(--sp-3);
  background: var(--c-danger-50);
  border-left: 3px solid var(--c-danger-500);
  border-radius: var(--r-sm);
  color: var(--c-danger-500);
  font-size: var(--fs-sm);
  white-space: pre-line;
}

.auth__foot {
  display: flex;
  justify-content: center;
  gap: var(--sp-2);
  margin-top: var(--sp-5);
  padding-top: var(--sp-5);
  border-top: 1px solid var(--border-default);
  font-size: var(--fs-sm);
}

.auth__note {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.auth__note code {
  color: var(--text-secondary);
}
</style>
