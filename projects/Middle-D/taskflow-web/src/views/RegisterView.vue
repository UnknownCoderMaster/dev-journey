<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toasts'
import AppButton from '@/components/ui/AppButton.vue'
import AppField from '@/components/ui/AppField.vue'

const auth = useAuthStore()
const toasts = useToastStore()
const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const confirm = ref('')
const formError = ref('')

/** Backend talabi: MinLength(6) */
const passwordTooShort = computed(
  () => password.value.length > 0 && password.value.length < 6,
)

const mismatch = computed(
  () => confirm.value.length > 0 && confirm.value !== password.value,
)

async function submit(): Promise<void> {
  formError.value = ''

  if (!fullName.value.trim()) {
    formError.value = "To'liq ismni kiriting"
    return
  }

  if (password.value.length < 6) {
    formError.value = "Parol kamida 6 belgidan iborat bo'lishi kerak"
    return
  }

  if (password.value !== confirm.value) {
    formError.value = 'Parollar mos kelmadi'
    return
  }

  try {
    await auth.register({
      fullName: fullName.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })

    toasts.success("Ro'yxatdan o'tdingiz")
    await router.push({ name: 'boards' })
  } catch (error) {
    if (error instanceof ApiError) {
      formError.value = error.message
    } else if (error instanceof Error) {
      formError.value = error.message
    } else {
      formError.value = "Ro'yxatdan o'tishda kutilmagan xato"
    }
  }
}
</script>

<template>
  <div class="auth">
    <section class="auth__panel">
      <header class="auth__head">
        <h1 class="auth__title">Ro'yxatdan o'tish</h1>
        <p class="auth__subtitle">Yangi hisob yaratib, doskalar bilan ishlashni boshlang</p>
      </header>

      <form class="auth__form" novalidate @submit.prevent="submit">
        <AppField
          v-model="fullName"
          label="To'liq ism"
          placeholder="Ism Familiya"
          autocomplete="name"
          :maxlength="256"
          required
        />

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
          autocomplete="new-password"
          hint="Kamida 6 belgi"
          :error="passwordTooShort ? 'Kamida 6 belgi kerak' : undefined"
          required
        />

        <AppField
          v-model="confirm"
          label="Parolni tasdiqlash"
          type="password"
          placeholder="••••••••"
          autocomplete="new-password"
          :error="mismatch ? 'Parollar mos kelmadi' : undefined"
          required
        />

        <p v-if="formError" class="auth__error" role="alert">{{ formError }}</p>

        <AppButton type="submit" variant="primary" block :loading="auth.loading">
          Hisob yaratish
        </AppButton>
      </form>

      <footer class="auth__foot">
        <span class="u-muted">Hisobingiz bormi?</span>
        <RouterLink :to="{ name: 'login' }">Kirish</RouterLink>
      </footer>
    </section>
  </div>
</template>

<style scoped>
.auth {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--sp-6) var(--sp-4);
  background: var(--bg-page);
}

.auth__panel {
  width: 100%;
  max-width: 392px;
  padding: var(--sp-8);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-sm);
}

.auth__head {
  margin-bottom: var(--sp-6);
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
</style>
