<template>
  <q-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
    <q-card class="confirm-dialog app-panel">
      <q-card-section class="confirm-heading">
        <q-icon :name="icon" :color="color" />
        <div>
          <h2>{{ title }}</h2>
          <p>{{ message }}</p>
        </div>
      </q-card-section>

      <q-card-actions class="confirm-actions">
        <q-btn flat :label="cancelLabel" @click="$emit('cancel')" />
        <q-btn :color="color" :label="confirmLabel" unelevated @click="$emit('confirm')" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  confirmLabel: {
    type: String,
    default: 'Confirmar'
  },
  cancelLabel: {
    type: String,
    default: 'Cancelar'
  },
  icon: {
    type: String,
    default: 'warning'
  },
  color: {
    type: String,
    default: 'negative'
  }
})

defineEmits(['update:modelValue', 'confirm', 'cancel'])
</script>

<style scoped>
.confirm-dialog {
  width: min(92vw, 30rem);
  overflow: hidden;
  border-radius: calc(var(--radius-app) + 0.35rem);
}

.confirm-heading {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 1.4rem);
}

.confirm-heading .q-icon {
  margin-top: 0.1rem;
  font-size: 1.8rem;
}

.confirm-heading h2,
.confirm-heading p {
  margin: 0;
}

.confirm-heading h2 {
  color: rgb(15 23 42);
  font-size: clamp(1.25rem, 4vw, 1.6rem);
  line-height: 1.1;
}

.confirm-heading p {
  margin-top: 0.45rem;
  color: rgb(71 85 105);
}

.confirm-actions {
  justify-content: space-between;
  gap: 0.55rem;
  padding: 1rem clamp(1rem, 3vw, 1.4rem);
  background: rgb(248 250 252 / 0.9);
}
</style>
