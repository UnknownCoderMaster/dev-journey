<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { attachmentsApi, commentsApi } from '@/api/resources'
import { useAuthStore } from '@/stores/auth'
import { useCardsStore } from '@/stores/cards'
import { useToastStore } from '@/stores/toasts'
import {
  describeDeadline,
  formatDateTime,
  formatFileSize,
  formatRelative,
} from '@/composables/useFormat'
import { STATUS_LABELS, STATUS_TONES } from '@/composables/useCardStatus'
import { CardStatus, type AttachmentUploadResult, type CardListItem, type CommentDto } from '@/types'
import AppAvatar from '@/components/ui/AppAvatar.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppField from '@/components/ui/AppField.vue'
import AppState from '@/components/ui/AppState.vue'

const props = defineProps<{
  card: CardListItem | null
}>()

const emit = defineEmits<{
  close: []
  deleted: [cardId: number]
}>()

const auth = useAuthStore()
const cards = useCardsStore()
const toasts = useToastStore()

/* ─── Izohlar ─────────────────────────────────────────── */

const comments = ref<CommentDto[]>([])
const commentsLoading = ref(false)
const commentsFailed = ref(false)
const draft = ref('')
const sending = ref(false)

/* ─── Fayllar ─────────────────────────────────────────── */

/**
 * Backend'da biriktirilgan fayllar ro'yxatini qaytaradigan endpoint yo'q —
 * faqat yuklash, havola olish va o'chirish bor. Shuning uchun bu yerda
 * faqat shu sessiyada yuklangan fayllar ko'rinadi.
 */
const uploaded = ref<AttachmentUploadResult[]>([])
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const MAX_SIZE = 10 * 1024 * 1024

const deadline = computed(() => (props.card ? describeDeadline(props.card.deadline) : null))

const statusOptions = [CardStatus.Todo, CardStatus.InProgress, CardStatus.Done] as const

async function loadComments(cardId: number): Promise<void> {
  commentsLoading.value = true
  commentsFailed.value = false
  try {
    comments.value = await commentsApi.list(cardId)
  } catch (error) {
    commentsFailed.value = true
    toasts.error(error)
  } finally {
    commentsLoading.value = false
  }
}

watch(
  () => props.card?.id,
  (cardId) => {
    comments.value = []
    uploaded.value = []
    draft.value = ''

    if (cardId !== undefined) {
      void loadComments(cardId)
    }
  },
  { immediate: true },
)

async function sendComment(): Promise<void> {
  const text = draft.value.trim()
  if (!text || !props.card) return

  sending.value = true
  try {
    const created = await commentsApi.create(props.card.id, text)

    // SignalR ham shu hodisani yuboradi, lekin o'zimizning ulanishimiz
    // uzilgan bo'lishi mumkin — shuning uchun javobni darhol qo'shamiz.
    if (!comments.value.some((c) => c.id === created.id)) {
      comments.value = [...comments.value, created]
      cards.bumpCommentsCount(props.card.id, 1)
    }

    draft.value = ''
  } catch (error) {
    toasts.error(error)
  } finally {
    sending.value = false
  }
}

async function removeComment(comment: CommentDto): Promise<void> {
  if (!props.card) return

  const confirmed = window.confirm("Izohni o'chirishni tasdiqlaysizmi?")
  if (!confirmed) return

  try {
    await commentsApi.remove(props.card.id, comment.id)
    comments.value = comments.value.filter((c) => c.id !== comment.id)
    cards.bumpCommentsCount(props.card.id, -1)
  } catch (error) {
    toasts.error(error)
  }
}

/** SignalR dan kelgan izohni qo'shadi (tashqaridan chaqiriladi). */
function applyIncomingComment(comment: CommentDto): void {
  if (comments.value.some((c) => c.id === comment.id)) return
  comments.value = [...comments.value, comment]
}

function applyRemovedComment(commentId: number): void {
  comments.value = comments.value.filter((c) => c.id !== commentId)
}

defineExpose({ applyIncomingComment, applyRemovedComment })

async function onFilePicked(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !props.card) return

  if (file.size === 0) {
    toasts.error(new Error("Fayl bo'sh"))
    input.value = ''
    return
  }

  if (file.size > MAX_SIZE) {
    toasts.error(new Error("Fayl hajmi 10 MB dan oshmasligi kerak"))
    input.value = ''
    return
  }

  uploading.value = true
  try {
    const result = await attachmentsApi.upload(props.card.id, file)
    uploaded.value = [...uploaded.value, result]
    cards.bumpAttachmentsCount(props.card.id, 1)
    toasts.success('Fayl yuklandi')
  } catch (error) {
    toasts.error(error)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function openAttachment(attachment: AttachmentUploadResult): Promise<void> {
  if (!props.card) return

  try {
    const { url } = await attachmentsApi.getUrl(props.card.id, attachment.id)
    window.open(url, '_blank', 'noopener,noreferrer')
  } catch (error) {
    toasts.error(error)
  }
}

async function removeAttachment(attachment: AttachmentUploadResult): Promise<void> {
  if (!props.card) return

  try {
    await attachmentsApi.remove(props.card.id, attachment.id)
    uploaded.value = uploaded.value.filter((a) => a.id !== attachment.id)
    cards.bumpAttachmentsCount(props.card.id, -1)
  } catch (error) {
    toasts.error(error)
  }
}

async function changeStatus(status: (typeof statusOptions)[number]): Promise<void> {
  if (!props.card || props.card.status === status) return

  try {
    await cards.moveTo(props.card.id, status)
  } catch (error) {
    toasts.error(error)
  }
}

async function removeCard(): Promise<void> {
  if (!props.card) return

  const confirmed = window.confirm(
    `"${props.card.title}" kartasi o'chiriladi. Davom etasizmi?`,
  )
  if (!confirmed) return

  const cardId = props.card.id
  try {
    await cards.remove(cardId)
    toasts.success("Karta o'chirildi")
    emit('deleted', cardId)
    emit('close')
  } catch (error) {
    toasts.error(error)
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="card" class="drawer" role="dialog" aria-modal="true" :aria-label="card.title">
        <div class="drawer__backdrop" @click="emit('close')" />

        <aside class="drawer__panel">
          <header class="drawer__head">
            <div class="drawer__head-main">
              <AppBadge :tone="STATUS_TONES[card.status]" dot>
                {{ STATUS_LABELS[card.status] }}
              </AppBadge>
              <h2 class="drawer__title">{{ card.title }}</h2>
            </div>

            <button type="button" class="drawer__close" aria-label="Yopish" @click="emit('close')">
              <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
                <path
                  d="M4 4l8 8M12 4l-8 8"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  fill="none"
                />
              </svg>
            </button>
          </header>

          <div class="drawer__body">
            <!-- Tavsif -->
            <section class="block">
              <h3 class="block__title">Tavsif</h3>
              <p v-if="card.description" class="block__text">{{ card.description }}</p>
              <p v-else class="block__text block__text--empty">Tavsif kiritilmagan</p>
            </section>

            <!-- Xossalar -->
            <section class="block">
              <h3 class="block__title">Xossalar</h3>
              <dl class="props">
                <dt>Mas'ul</dt>
                <dd>
                  <span v-if="card.assignee" class="u-row">
                    <AppAvatar :name="card.assignee" />
                    {{ card.assignee }}
                  </span>
                  <span v-else class="u-muted">Belgilanmagan</span>
                </dd>

                <dt>Muddat</dt>
                <dd>
                  <AppBadge v-if="deadline" :tone="deadline.tone" dot>
                    {{ deadline.text }}
                  </AppBadge>
                  <span v-else class="u-muted">Yo'q</span>
                </dd>

                <dt>Yaratilgan</dt>
                <dd>{{ formatDateTime(card.createdAt) }}</dd>
              </dl>
            </section>

            <!-- Status -->
            <section class="block">
              <h3 class="block__title">Statusni o'zgartirish</h3>
              <div class="status-row">
                <AppButton
                  v-for="option in statusOptions"
                  :key="option"
                  size="sm"
                  :variant="card.status === option ? 'primary' : 'secondary'"
                  :disabled="cards.pending.has(card.id)"
                  @click="changeStatus(option)"
                >
                  {{ STATUS_LABELS[option] }}
                </AppButton>
              </div>
            </section>

            <!-- Fayllar -->
            <section class="block">
              <h3 class="block__title">
                Fayllar
                <span class="block__hint">· jami {{ card.attachmentsCount }}</span>
              </h3>

              <p class="block__note">
                Backend biriktirilgan fayllar ro'yxatini qaytaradigan endpoint
                bermaydi, shuning uchun bu yerda faqat shu sessiyada yuklanganlar
                ko'rinadi.
              </p>

              <ul v-if="uploaded.length > 0" class="files">
                <li v-for="file in uploaded" :key="file.id" class="files__row">
                  <button type="button" class="files__name u-truncate" @click="openAttachment(file)">
                    {{ file.fileName }}
                  </button>
                  <span class="files__size">{{ formatFileSize(file.fileSize) }}</span>
                  <button
                    type="button"
                    class="files__remove"
                    aria-label="O'chirish"
                    @click="removeAttachment(file)"
                  >
                    <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
                      <path
                        d="M4 4l8 8M12 4l-8 8"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        fill="none"
                      />
                    </svg>
                  </button>
                </li>
              </ul>

              <input
                ref="fileInput"
                type="file"
                class="u-sr-only"
                @change="onFilePicked"
              />

              <AppButton
                size="sm"
                variant="secondary"
                :loading="uploading"
                @click="fileInput?.click()"
              >
                Fayl yuklash
              </AppButton>
            </section>

            <!-- Izohlar -->
            <section class="block">
              <h3 class="block__title">
                Izohlar
                <span class="block__hint">· {{ comments.length }}</span>
              </h3>

              <AppState v-if="commentsLoading" kind="loading" :rows="2" />

              <AppState
                v-else-if="commentsFailed"
                kind="error"
                title="Izohlar yuklanmadi"
              >
                <AppButton size="sm" variant="secondary" @click="loadComments(card.id)">
                  Qayta urinish
                </AppButton>
              </AppState>

              <p v-else-if="comments.length === 0" class="block__text block__text--empty">
                Hali izoh yo'q
              </p>

              <ul v-else class="comments">
                <li v-for="comment in comments" :key="comment.id" class="comment">
                  <AppAvatar :name="comment.authorName" />

                  <div class="comment__main">
                    <div class="comment__meta">
                      <span class="comment__author">{{ comment.authorName }}</span>
                      <time :datetime="comment.createdAt" class="comment__time">
                        {{ formatRelative(comment.createdAt) }}
                      </time>
                    </div>
                    <p class="comment__text">{{ comment.content }}</p>
                  </div>

                  <button
                    v-if="comment.authorId === auth.user?.id"
                    type="button"
                    class="comment__remove"
                    aria-label="Izohni o'chirish"
                    @click="removeComment(comment)"
                  >
                    <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
                      <path
                        d="M4 4l8 8M12 4l-8 8"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        fill="none"
                      />
                    </svg>
                  </button>
                </li>
              </ul>

              <form class="comment-form" @submit.prevent="sendComment">
                <AppField
                  v-model="draft"
                  label="Yangi izoh"
                  placeholder="Izoh yozing…"
                  multiline
                  :rows="3"
                  :maxlength="2000"
                  hint="Ctrl + Enter bilan yuborish"
                  @keydown.ctrl.enter.prevent="sendComment"
                />

                <div class="comment-form__actions">
                  <AppButton
                    type="submit"
                    size="sm"
                    variant="primary"
                    :loading="sending"
                    :disabled="draft.trim().length === 0"
                  >
                    Yuborish
                  </AppButton>
                </div>
              </form>
            </section>
          </div>

          <footer class="drawer__foot">
            <AppButton variant="danger" size="sm" @click="removeCard">
              Kartani o'chirish
            </AppButton>
            <AppButton variant="ghost" size="sm" @click="emit('close')">Yopish</AppButton>
          </footer>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: flex;
  justify-content: flex-end;
}

.drawer__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(21, 24, 29, 0.38);
}

.drawer__panel {
  position: relative;
  display: flex;
  flex-direction: column;
  width: min(480px, 100vw);
  background: var(--bg-surface);
  border-left: 1px solid var(--border-default);
  box-shadow: var(--sh-lg);
}

.drawer__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-4);
  padding: var(--sp-5);
  border-bottom: 1px solid var(--border-default);
}

.drawer__head-main {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  align-items: flex-start;
}

.drawer__title {
  font-size: var(--fs-lg);
  line-height: var(--lh-tight);
}

.drawer__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  color: var(--text-muted);
  cursor: pointer;
}

.drawer__close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.drawer__body {
  flex: 1;
  overflow-y: auto;
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-6);
}

.drawer__foot {
  display: flex;
  justify-content: space-between;
  gap: var(--sp-2);
  padding: var(--sp-4) var(--sp-5);
  border-top: 1px solid var(--border-default);
  background: var(--bg-subtle);
}

/* ─── Bloklar ───────────────────────────── */

.block {
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
}

.block__title {
  font-size: var(--fs-sm);
  font-weight: var(--fw-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.block__hint {
  font-weight: var(--fw-normal);
  text-transform: none;
  letter-spacing: 0;
}

.block__text {
  font-size: var(--fs-base);
  line-height: var(--lh-relaxed);
  white-space: pre-line;
}

.block__text--empty {
  color: var(--text-muted);
  font-style: italic;
}

.block__note {
  padding: var(--sp-2) var(--sp-3);
  background: var(--c-warning-50);
  border-left: 3px solid var(--c-warning-500);
  border-radius: var(--r-sm);
  color: var(--text-secondary);
  font-size: var(--fs-xs);
  line-height: var(--lh-relaxed);
}

.props {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: var(--sp-2) var(--sp-4);
  margin: 0;
  align-items: center;
}

.props dt {
  color: var(--text-muted);
  font-size: var(--fs-sm);
}

.props dd {
  margin: 0;
  font-size: var(--fs-base);
}

.status-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
}

/* ─── Fayllar ───────────────────────────── */

.files {
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
  margin: 0;
  padding: 0;
  list-style: none;
}

.files__row {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  background: var(--bg-subtle);
  border: 1px solid var(--border-default);
  border-radius: var(--r-sm);
}

.files__name {
  flex: 1;
  min-width: 0;
  background: none;
  border: none;
  padding: 0;
  color: var(--text-accent);
  font-size: var(--fs-sm);
  text-align: left;
  cursor: pointer;
}

.files__name:hover {
  text-decoration: underline;
}

.files__size {
  color: var(--text-muted);
  font-size: var(--fs-xs);
  font-variant-numeric: tabular-nums;
}

.files__remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  color: var(--text-muted);
  cursor: pointer;
}

.files__remove:hover {
  background: var(--c-danger-50);
  color: var(--c-danger-500);
}

/* ─── Izohlar ───────────────────────────── */

.comments {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

.comment {
  display: flex;
  gap: var(--sp-3);
  align-items: flex-start;
}

.comment__main {
  flex: 1;
  min-width: 0;
}

.comment__meta {
  display: flex;
  align-items: baseline;
  gap: var(--sp-2);
}

.comment__author {
  font-size: var(--fs-sm);
  font-weight: var(--fw-medium);
}

.comment__time {
  color: var(--text-muted);
  font-size: var(--fs-xs);
}

.comment__text {
  margin-top: var(--sp-1);
  font-size: var(--fs-base);
  line-height: var(--lh-relaxed);
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.comment__remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  background: transparent;
  border: none;
  border-radius: var(--r-sm);
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--transition);
}

.comment:hover .comment__remove,
.comment__remove:focus-visible {
  opacity: 1;
}

.comment__remove:hover {
  background: var(--c-danger-50);
  color: var(--c-danger-500);
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
  padding-top: var(--sp-4);
  border-top: 1px solid var(--border-default);
}

.comment-form__actions {
  display: flex;
  justify-content: flex-end;
}

/* ─── Animatsiya ────────────────────────── */

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 160ms ease;
}

.drawer-enter-active .drawer__panel,
.drawer-leave-active .drawer__panel {
  transition: transform 160ms cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer__panel,
.drawer-leave-to .drawer__panel {
  transform: translateX(24px);
}
</style>
