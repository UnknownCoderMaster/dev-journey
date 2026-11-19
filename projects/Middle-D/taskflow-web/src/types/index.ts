/**
 * Backend shartnomasi — TaskFlow.API dan aynan ko'chirilgan.
 * Har bir tur yonida u qaysi endpoint'dan kelishi yozilgan.
 */

/* ─── Auth ──────────────────────────────────────────────── */

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  fullName: string
  email: string
  password: string
}

/** POST /api/auth/login */
export interface TokenResponse {
  accessToken: string
  refreshToken: string
  expiresAt: string
}

/** POST /api/auth/register */
export interface RegisterResponse {
  message: string
  userId: number
}

/** JWT payload — backend TokenService.GenerateAccessToken dagi claim'lar */
export interface JwtPayload {
  /** ClaimTypes.NameIdentifier */
  nameid?: string
  /** ClaimTypes.Email */
  email?: string
  /** ClaimTypes.Name */
  unique_name?: string
  /** ClaimTypes.Role */
  role?: string
  exp?: number
  iss?: string
  aud?: string
  [key: string]: unknown
}

export interface CurrentUser {
  id: number
  fullName: string
  email: string
  role: string
}

/* ─── Board ─────────────────────────────────────────────── */

/** GET /api/boards — controller'dagi anonim projeksiya */
export interface BoardListItem {
  id: number
  name: string
  description: string | null
  /** Projeksiyada Owner — FullName satri, obyekt emas */
  owner: string | null
  cardsCount: number
  createdAt: string
}

export interface CreateBoardRequest {
  name: string
  description?: string | null
}

/* ─── Card ──────────────────────────────────────────────── */

/**
 * Backend enum: Todo = 0, InProgress = 1, Done = 2.
 * JsonStringEnumConverter sozlanmagan, shuning uchun REST javoblarida
 * raqam keladi. SignalR hodisalarida esa `.ToString()` qilingan —
 * ya'ni satr keladi. Ikkisini ham qabul qilamiz.
 */
export const CardStatus = {
  Todo: 0,
  InProgress: 1,
  Done: 2,
} as const

export type CardStatusValue = (typeof CardStatus)[keyof typeof CardStatus]

export type CardStatusName = 'Todo' | 'InProgress' | 'Done'

/** GET /api/boards/{boardId}/cards */
export interface CardListItem {
  id: number
  title: string
  description: string | null
  status: CardStatusValue
  deadline: string | null
  /** Projeksiyada Assignee — FullName satri yoki null */
  assignee: string | null
  commentsCount: number
  attachmentsCount: number
  createdAt: string
}

export interface CreateCardRequest {
  title: string
  description?: string | null
  deadline?: string | null
  assigneeId?: number | null
}

/* ─── Comment ───────────────────────────────────────────── */

/** GET /api/cards/{cardId}/comments */
export interface CommentDto {
  id: number
  content: string
  authorId: number
  authorName: string
  createdAt: string
}

export interface CreateCommentRequest {
  content: string
}

/* ─── Attachment ────────────────────────────────────────── */

/** POST /api/cards/{cardId}/attachments javobi */
export interface AttachmentUploadResult {
  id: number
  fileName: string
  fileSize: number
  uploadedAt: string
}

/** GET /api/cards/{cardId}/attachments/{id}/url */
export interface AttachmentUrlResult {
  url: string
  expiresIn: string
}

/* ─── SignalR hodisalari ────────────────────────────────── */

export interface CardCreatedEvent {
  id: number
  title: string
  /** Hub'da card.Status uzatiladi — raqam */
  status: CardStatusValue
}

export interface CardStatusUpdatedEvent {
  cardId: number
  /** Hub'da `.ToString()` qilingan — "Todo" / "InProgress" / "Done" */
  newStatus: CardStatusName
}

export interface CardDeletedEvent {
  cardId: number
}

export interface CommentCreatedEvent {
  cardId: number
  comment: CommentDto
}

export interface CommentDeletedEvent {
  cardId: number
  commentId: number
}
