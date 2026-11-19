/**
 * Endpoint'lar — har biri backend'dagi aniq route'ga mos.
 * Bu fayl API shartnomasining yagona ro'yxati bo'lib xizmat qiladi.
 */
import { http } from './client'
import type {
  AttachmentUploadResult,
  AttachmentUrlResult,
  BoardListItem,
  CardListItem,
  CardStatusValue,
  CommentDto,
  CreateBoardRequest,
  CreateCardRequest,
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
} from '@/types'

/* ─── Auth ──────────────────────────────────────────────── */

export const authApi = {
  /** POST /api/auth/login */
  login: (body: LoginRequest) => http.post<TokenResponse>('/auth/login', body),

  /** POST /api/auth/register */
  register: (body: RegisterRequest) =>
    http.post<RegisterResponse>('/auth/register', body),
}

/* ─── Boards ────────────────────────────────────────────── */

export const boardsApi = {
  /** GET /api/boards — 5 daqiqa serverda keshlanadi */
  list: (signal?: AbortSignal) => http.get<BoardListItem[]>('/boards', signal),

  /** POST /api/boards */
  create: (body: CreateBoardRequest) => http.post<unknown>('/boards', body),
}

/* ─── Cards ─────────────────────────────────────────────── */

export const cardsApi = {
  /** GET /api/boards/{boardId}/cards */
  list: (boardId: number, signal?: AbortSignal) =>
    http.get<CardListItem[]>(`/boards/${boardId}/cards`, signal),

  /** POST /api/boards/{boardId}/cards */
  create: (boardId: number, body: CreateCardRequest) =>
    http.post<unknown>(`/boards/${boardId}/cards`, body),

  /**
   * PATCH /api/boards/{boardId}/cards/{cardId}/status
   * Enum raqam sifatida yuboriladi — backend'da JsonStringEnumConverter yo'q.
   */
  updateStatus: (boardId: number, cardId: number, status: CardStatusValue) =>
    http.patch<{ message: string; status: number }>(
      `/boards/${boardId}/cards/${cardId}/status`,
      { status },
    ),

  /** DELETE /api/boards/{boardId}/cards/{cardId} */
  remove: (boardId: number, cardId: number) =>
    http.delete<void>(`/boards/${boardId}/cards/${cardId}`),
}

/* ─── Comments ──────────────────────────────────────────── */

export const commentsApi = {
  /** GET /api/cards/{cardId}/comments */
  list: (cardId: number, signal?: AbortSignal) =>
    http.get<CommentDto[]>(`/cards/${cardId}/comments`, signal),

  /** POST /api/cards/{cardId}/comments */
  create: (cardId: number, content: string) =>
    http.post<CommentDto>(`/cards/${cardId}/comments`, { content }),

  /** DELETE /api/cards/{cardId}/comments/{commentId} — faqat muallif */
  remove: (cardId: number, commentId: number) =>
    http.delete<void>(`/cards/${cardId}/comments/${commentId}`),
}

/* ─── Attachments ───────────────────────────────────────── */

export const attachmentsApi = {
  /**
   * POST /api/cards/{cardId}/attachments
   * Backend IFormFile parametrini "file" nomi bilan kutadi.
   */
  upload: (cardId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.upload<AttachmentUploadResult>(`/cards/${cardId}/attachments`, form)
  },

  /** GET /api/cards/{cardId}/attachments/{id}/url — MinIO presigned havolasi */
  getUrl: (cardId: number, attachmentId: number) =>
    http.get<AttachmentUrlResult>(`/cards/${cardId}/attachments/${attachmentId}/url`),

  /** DELETE /api/cards/{cardId}/attachments/{id} */
  remove: (cardId: number, attachmentId: number) =>
    http.delete<void>(`/cards/${cardId}/attachments/${attachmentId}`),
}
