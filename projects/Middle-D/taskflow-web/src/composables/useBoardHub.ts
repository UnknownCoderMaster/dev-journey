import { onScopeDispose, readonly, ref } from 'vue'
import {
  HttpTransportType,
  HubConnectionBuilder,
  HubConnectionState,
  LogLevel,
  type HubConnection,
} from '@microsoft/signalr'
import { useAuthStore } from '@/stores/auth'
import { useCardsStore } from '@/stores/cards'
import { useToastStore } from '@/stores/toasts'
import { normalizeStatus } from './useCardStatus'
import type {
  CardDeletedEvent,
  CardStatusUpdatedEvent,
  CommentCreatedEvent,
  CommentDeletedEvent,
} from '@/types'

export type HubStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

export interface BoardHubHandlers {
  onCardCreated?: () => void
  onCommentCreated?: (event: CommentCreatedEvent) => void
  onCommentDeleted?: (event: CommentDeletedEvent) => void
}

/**
 * TaskHub bilan ulanishni boshqaradi.
 *
 * Backend hub'ni `/hubs/tasks` da e'lon qilgan va tokenni query string
 * dan ham qabul qiladi (`Program.cs` → `OnMessageReceived`). Bu WebSocket
 * uchun zarur, chunki brauzer WebSocket so'roviga header qo'sha olmaydi.
 */
export function useBoardHub(handlers: BoardHubHandlers = {}) {
  const auth = useAuthStore()
  const cards = useCardsStore()
  const toasts = useToastStore()

  const status = ref<HubStatus>('disconnected')
  const lastEventAt = ref<Date | null>(null)

  let connection: HubConnection | null = null
  let joinedBoardId: number | null = null

  function markEvent(): void {
    lastEventAt.value = new Date()
  }

  function build(): HubConnection {
    return new HubConnectionBuilder()
      .withUrl('/hubs/tasks', {
        accessTokenFactory: () => auth.token ?? '',
        // WebSocket bo'lmasa SSE ga tushadi. Long polling'ni ataylab
        // qoldirmadim: agar WebSocket ishlamasa, buni bilish kerak —
        // ko'pincha sababi reverse proxy'da upgrade header'i yo'qligi.
        transport: HttpTransportType.WebSockets | HttpTransportType.ServerSentEvents,
      })
      .withAutomaticReconnect([0, 2000, 5000, 10000, 20000])
      .configureLogging(import.meta.env.DEV ? LogLevel.Warning : LogLevel.Error)
      .build()
  }

  function attachHandlers(hub: HubConnection): void {
    hub.on('CardCreated', () => {
      markEvent()
      handlers.onCardCreated?.()
    })

    hub.on('CardStatusUpdated', (event: CardStatusUpdatedEvent) => {
      markEvent()
      // Hub satr yuboradi — normalizeStatus ikkisini ham tushunadi
      cards.applyStatusFromEvent(event.cardId, normalizeStatus(event.newStatus))
    })

    hub.on('CardDeleted', (event: CardDeletedEvent) => {
      markEvent()
      cards.applyDeleteFromEvent(event.cardId)
    })

    hub.on('CommentCreated', (event: CommentCreatedEvent) => {
      markEvent()
      cards.bumpCommentsCount(event.cardId, 1)
      handlers.onCommentCreated?.(event)
    })

    hub.on('CommentDeleted', (event: CommentDeletedEvent) => {
      markEvent()
      cards.bumpCommentsCount(event.cardId, -1)
      handlers.onCommentDeleted?.(event)
    })

    hub.onreconnecting(() => {
      status.value = 'reconnecting'
    })

    hub.onreconnected(async () => {
      status.value = 'connected'
      // Qayta ulanishda guruh a'zoligi saqlanmaydi — qaytadan qo'shilamiz
      if (joinedBoardId !== null) {
        try {
          await hub.invoke('JoinBoard', String(joinedBoardId))
        } catch {
          /* keyingi urinishda tiklanadi */
        }
      }
    })

    hub.onclose(() => {
      status.value = 'disconnected'
    })
  }

  async function connect(boardId: number): Promise<void> {
    if (!auth.token) return

    if (connection && connection.state === HubConnectionState.Connected) {
      await join(boardId)
      return
    }

    connection = build()
    attachHandlers(connection)

    status.value = 'connecting'
    try {
      await connection.start()
      status.value = 'connected'
      await join(boardId)
    } catch (error) {
      status.value = 'disconnected'
      // Realtime ishlamasa ham ilova ishlashda davom etadi —
      // shuning uchun bu ogohlantirish, xato emas.
      toasts.warning(
        "Real vaqt ulanishi o'rnatilmadi. Ma'lumot avtomatik yangilanmaydi.",
      )
      if (import.meta.env.DEV) console.warn('[hub] start failed', error)
    }
  }

  async function join(boardId: number): Promise<void> {
    if (!connection || connection.state !== HubConnectionState.Connected) return

    if (joinedBoardId !== null && joinedBoardId !== boardId) {
      try {
        await connection.invoke('LeaveBoard', String(joinedBoardId))
      } catch {
        /* ulanish uzilgan bo'lsa ahamiyatsiz */
      }
    }

    try {
      await connection.invoke('JoinBoard', String(boardId))
      joinedBoardId = boardId
    } catch (error) {
      if (import.meta.env.DEV) console.warn('[hub] JoinBoard failed', error)
    }
  }

  async function disconnect(): Promise<void> {
    if (!connection) return

    const hub = connection
    connection = null

    if (joinedBoardId !== null && hub.state === HubConnectionState.Connected) {
      try {
        await hub.invoke('LeaveBoard', String(joinedBoardId))
      } catch {
        /* yopilayotganda ahamiyatsiz */
      }
    }

    joinedBoardId = null
    status.value = 'disconnected'

    try {
      await hub.stop()
    } catch {
      /* ahamiyatsiz */
    }
  }

  onScopeDispose(() => {
    void disconnect()
  })

  return {
    status: readonly(status),
    lastEventAt: readonly(lastEventAt),
    connect,
    disconnect,
  }
}
