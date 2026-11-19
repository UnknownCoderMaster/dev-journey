import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api/resources'
import { setTokenProvider, setUnauthorizedHandler } from '@/api/client'
import type { CurrentUser, JwtPayload, LoginRequest, RegisterRequest } from '@/types'

const TOKEN_KEY = 'taskflow.accessToken'
const REFRESH_KEY = 'taskflow.refreshToken'

/**
 * JWT payload'ini o'qiydi.
 *
 * Diqqat: bu faqat **ko'rsatish** uchun — foydalanuvchi ismini header'da
 * chiqarish uchun. Imzo tekshirilmaydi va tekshirilishi ham kerak emas:
 * haqiqiy qarorlarni har doim server qabul qiladi.
 */
function decodeToken(token: string): JwtPayload | null {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null

    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(
      normalized.length + ((4 - (normalized.length % 4)) % 4),
      '=',
    )

    const json = decodeURIComponent(
      atob(padded)
        .split('')
        .map((ch) => `%${ch.charCodeAt(0).toString(16).padStart(2, '0')}`)
        .join(''),
    )

    return JSON.parse(json) as JwtPayload
  } catch {
    return null
  }
}

/**
 * .NET ClaimTypes URI shaklida ham kelishi mumkin, shuning uchun
 * ikki variantni ham qaraymiz.
 */
function claim(payload: JwtPayload, short: string, uri: string): string | undefined {
  const value = payload[short] ?? payload[uri]
  return typeof value === 'string' ? value : undefined
}

function toUser(payload: JwtPayload): CurrentUser | null {
  const id = claim(
    payload,
    'nameid',
    'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier',
  )
  if (!id) return null

  return {
    id: Number(id),
    fullName:
      claim(payload, 'unique_name', 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name') ??
      'Foydalanuvchi',
    email:
      claim(
        payload,
        'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
      ) ?? '',
    role:
      claim(payload, 'role', 'http://schemas.microsoft.com/ws/2008/06/identity/claims/role') ??
      'Member',
  }
}

function isExpired(payload: JwtPayload): boolean {
  if (typeof payload.exp !== 'number') return false
  // 30 soniya zapas — soat farqi va tarmoq kechikishi uchun
  return payload.exp * 1000 <= Date.now() + 30_000
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<CurrentUser | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => token.value !== null && user.value !== null)

  function apply(accessToken: string, refreshToken?: string): boolean {
    const payload = decodeToken(accessToken)
    if (!payload || isExpired(payload)) return false

    const parsed = toUser(payload)
    if (!parsed) return false

    token.value = accessToken
    user.value = parsed

    localStorage.setItem(TOKEN_KEY, accessToken)
    if (refreshToken) {
      localStorage.setItem(REFRESH_KEY, refreshToken)
    }

    return true
  }

  function clear(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  /** Sahifa yangilanganda saqlangan tokenni tiklaydi. */
  function restore(): void {
    const saved = localStorage.getItem(TOKEN_KEY)
    if (!saved) return

    if (!apply(saved)) {
      // Muddati tugagan yoki buzilgan token — saqlab o'tirishdan foyda yo'q
      clear()
    }
  }

  async function login(credentials: LoginRequest): Promise<void> {
    loading.value = true
    try {
      const response = await authApi.login(credentials)

      if (!apply(response.accessToken, response.refreshToken)) {
        throw new Error("Serverdan kelgan token o'qilmadi")
      }
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterRequest): Promise<void> {
    loading.value = true
    try {
      await authApi.register(payload)
      // Backend register'da token qaytarmaydi — darhol login qilamiz
      await login({ email: payload.email, password: payload.password })
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    clear()
  }

  // HTTP mijoz tokenni va 401 holatini shu store'dan oladi
  setTokenProvider(() => token.value)
  setUnauthorizedHandler(() => clear())

  return {
    token,
    user,
    loading,
    isAuthenticated,
    restore,
    login,
    register,
    logout,
  }
})
