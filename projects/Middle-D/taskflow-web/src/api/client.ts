/**
 * HTTP mijoz — fetch ustidagi yupqa qatlam.
 *
 * Vazifalari:
 *   - Authorization header'ini qo'shish
 *   - 401 da sessiyani tozalash va login'ga yuborish
 *   - backend qaytaradigan turli xato shakllarini bitta turga keltirish
 */

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

/** 401 kelganda chaqiriladi — auth store o'zini shu yerga ulaydi. */
let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler
}

let tokenProvider: () => string | null = () => null

export function setTokenProvider(provider: () => string | null): void {
  tokenProvider = provider
}

export class ApiError extends Error {
  readonly status: number
  readonly payload: unknown

  constructor(status: number, message: string, payload?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }

  get isValidation(): boolean {
    return this.status === 400 || this.status === 422
  }

  get isConflict(): boolean {
    return this.status === 409
  }

  get isNotFound(): boolean {
    return this.status === 404
  }
}

/**
 * Xato xabarini chiqarib oladi. Backend uch xil shaklda javob beradi:
 *   - { message: "..." }           — AuthController, Comments
 *   - "Fayl bo'sh"                 — Attachments, Cards (oddiy satr)
 *   - ProblemDetails / ModelState  — [ApiController] validatsiyasi
 */
function extractMessage(status: number, body: unknown): string {
  if (typeof body === 'string' && body.trim().length > 0) {
    return body
  }

  if (body && typeof body === 'object') {
    const obj = body as Record<string, unknown>

    if (typeof obj.message === 'string') return obj.message
    if (typeof obj.detail === 'string') return obj.detail

    // ModelState: { errors: { Email: ["..."], Password: ["..."] } }
    if (obj.errors && typeof obj.errors === 'object') {
      const messages = Object.values(obj.errors as Record<string, unknown>)
        .flatMap((v) => (Array.isArray(v) ? v : [v]))
        .filter((v): v is string => typeof v === 'string')

      if (messages.length > 0) return messages.join('\n')
    }

    if (typeof obj.title === 'string') return obj.title
  }

  const fallback: Record<number, string> = {
    400: "So'rov noto'g'ri",
    401: 'Sessiya tugagan — qaytadan kiring',
    403: "Bu amal uchun ruxsatingiz yo'q",
    404: 'Topilmadi',
    409: 'Ziddiyat: bunday yozuv allaqachon mavjud',
    500: 'Serverda kutilmagan xato',
    502: "Server javob bermadi",
    503: 'Server vaqtincha ishlamayapti',
  }

  return fallback[status] ?? `Xato: ${status}`
}

async function readBody(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) return null

  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  /** FormData yuborilganda Content-Type ni brauzer o'zi qo'yadi */
  raw?: boolean
  signal?: AbortSignal
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, raw = false, signal } = options

  const headers: Record<string, string> = {}

  const token = tokenProvider()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  let payload: BodyInit | undefined
  if (body !== undefined && body !== null) {
    if (raw) {
      payload = body as BodyInit
    } else {
      headers['Content-Type'] = 'application/json'
      payload = JSON.stringify(body)
    }
  }

  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, { method, headers, body: payload, signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    throw new ApiError(
      0,
      "Serverga ulanib bo'lmadi. Backend ishlab turganini tekshiring.",
      error,
    )
  }

  if (response.status === 401) {
    onUnauthorized?.()
    throw new ApiError(401, extractMessage(401, await readBody(response)))
  }

  if (!response.ok) {
    const parsed = await readBody(response)
    throw new ApiError(response.status, extractMessage(response.status, parsed), parsed)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const parsed = await readBody(response)
  return parsed as T
}

export const http = {
  get: <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),

  post: <T>(path: string, body?: unknown, signal?: AbortSignal) =>
    request<T>(path, { method: 'POST', body, signal }),

  patch: <T>(path: string, body?: unknown, signal?: AbortSignal) =>
    request<T>(path, { method: 'PATCH', body, signal }),

  put: <T>(path: string, body?: unknown, signal?: AbortSignal) =>
    request<T>(path, { method: 'PUT', body, signal }),

  delete: <T>(path: string, signal?: AbortSignal) =>
    request<T>(path, { method: 'DELETE', signal }),

  upload: <T>(path: string, form: FormData, signal?: AbortSignal) =>
    request<T>(path, { method: 'POST', body: form, raw: true, signal }),
}
