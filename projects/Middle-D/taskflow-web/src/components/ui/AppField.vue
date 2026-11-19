<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    modelValue: string
    type?: 'text' | 'email' | 'password' | 'datetime-local' | 'search'
    placeholder?: string
    hint?: string
    error?: string
    required?: boolean
    disabled?: boolean
    autocomplete?: string
    /** Bir qatorli input o'rniga textarea */
    multiline?: boolean
    rows?: number
    maxlength?: number
  }>(),
  {
    type: 'text',
    required: false,
    disabled: false,
    multiline: false,
    rows: 3,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const id = useId()
const hintId = computed(() => `${id}-hint`)
const errorId = computed(() => `${id}-error`)

const describedBy = computed(() => {
  const ids: string[] = []
  if (props.error) ids.push(errorId.value)
  else if (props.hint) ids.push(hintId.value)
  return ids.length > 0 ? ids.join(' ') : undefined
})

function onInput(event: Event): void {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="field">
    <label :for="id" class="field__label">
      {{ label }}
      <span v-if="required" class="field__required" aria-hidden="true">*</span>
    </label>

    <textarea
      v-if="multiline"
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :rows="rows"
      :maxlength="maxlength"
      :required="required"
      :disabled="disabled"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="describedBy"
      class="field__control field__control--area"
      @input="onInput"
    />

    <input
      v-else
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="describedBy"
      class="field__control"
      @input="onInput"
    />

    <p v-if="error" :id="errorId" class="field__error" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="hintId" class="field__hint">{{ hint }}</p>
  </div>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.field__label {
  font-size: var(--fs-sm);
  font-weight: var(--fw-medium);
  color: var(--text-secondary);
}

.field__required {
  color: var(--c-danger-500);
}

.field__control {
  width: 100%;
  min-height: 34px;
  padding: 0 var(--sp-3);
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--r-md);
  color: var(--text-primary);
  font-size: var(--fs-base);
  transition:
    border-color var(--transition),
    box-shadow var(--transition);
}

.field__control--area {
  padding: var(--sp-2) var(--sp-3);
  line-height: var(--lh-normal);
  resize: vertical;
}

.field__control::placeholder {
  color: var(--text-muted);
}

.field__control:hover:not(:disabled) {
  border-color: var(--c-gray-400);
}

.field__control:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: var(--ring-focus);
}

.field__control:disabled {
  background: var(--bg-subtle);
  color: var(--text-muted);
  cursor: not-allowed;
}

.field__control[aria-invalid='true'] {
  border-color: var(--c-danger-500);
}

.field__control[aria-invalid='true']:focus {
  box-shadow: 0 0 0 3px var(--c-danger-50);
}

.field__hint,
.field__error {
  font-size: var(--fs-xs);
}

.field__hint {
  color: var(--text-muted);
}

.field__error {
  color: var(--c-danger-500);
  white-space: pre-line;
}
</style>
